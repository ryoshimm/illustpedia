import copy
from collections import OrderedDict

from django.views import generic
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import IPUser, Artist
from taggit.models import Tag
from itertools import chain


# Form
class AccountCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = IPUser
        fields = ("username", "nickname", "email")


class ArtistCreateForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ("artist_id", "artist_name", "tags")


class TagSearchForm(forms.Form):
    tag_list = forms.CharField(label="検索タグ", max_length=100)


# View
class IndexView(generic.TemplateView):
    template_name = 'I000_index.html'


class LoginView(generic.FormView):
    template_name = 'I001_login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('general:top')

    def form_valid(self, form):
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        login(user=user, request=self.request)
        return super(LoginView, self).form_valid(form)


class LogoutView(generic.View):
    def get(self, request, *args, **kwargs):
        logout(self.request)
        return redirect('general:login')


class AccountCreateView(generic.CreateView):
    template_name = 'I002_account_create.html'
    form_class = AccountCreateForm
    success_url = reverse_lazy('general:top')

    def done(self, request, cleaned_data):
        obj = AccountCreateForm(request.POST).save(commit=False)
        obj.created_by = self.request.user
        obj.save()

        # ユーザを作成してログイン処理し、トップに遷移する　一時退避
        # user = authenticate(username=cleaned_data['username'],
        #                     password=cleaned_data['password1'])
        # login(self.request, user)
        # return redirect(reverse('general:top', args=(), kwargs={}))

    def get_success_url(self):
            return reverse_lazy('general:login')


class TopView(generic.FormView):
    template_name = 'I003_top.html'
    form_class = TagSearchForm
    tag_list = None
    # success_url = reverse('general:tag_search', kwargs={'tag_list': 10})

    def get_context_data(self, **kwargs):
        context = super(TopView, self).get_context_data(**kwargs)
        context['artist_list'] = Artist.objects.all()
        context['all_tag_list'] = Tag.objects.all()
        return context

    def form_valid(self, form):
        tag_list = form.cleaned_data['tag_list']
        self.success_url = reverse('general:tag_search', kwargs={'tag_list': tag_list})
        return super(TopView, self).form_valid(form)


class AccountView(generic.TemplateView):
    template_name = 'I004_account.html'

    def get_context_data(self, **kwargs):
        context = super(AccountView, self).get_context_data(**kwargs)
        context['artist_list'] = self.request.user.fav_artist.all()
        return context


class ArtistCreateView(generic.CreateView):
    template_name = 'I005_artist_create.html'
    form_class = ArtistCreateForm

    def get_success_url(self):
        return reverse('general:artist_detail', args=[self.object.id])


class ArtistDetailView(generic.DetailView):
    template_name = 'I006_artist_detail.html'
    model = Artist, Tag

    def get_queryset(self):
        self.queryset = Artist.objects.all()
        return super(ArtistDetailView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(ArtistDetailView, self).get_context_data(**kwargs)
        context['artist'] = self.get_object()
        context['tag_list'] = self.get_object().tags.all()
        flag_fav = False
        if self.request.user.fav_artist.all().filter(artist_id=self.get_object().artist_id):
            flag_fav = True
        context['flag_fav'] = flag_fav
        return context

    def post(self, request, *args, **kwargs):
        artist_list = self.request.user.fav_artist
        artist_list.add(self.get_object())
        return redirect("general:artist_detail", pk=self.kwargs.get("pk"))


class TagSearchView(generic.TemplateView):
    template_name = 'I008_tag_search.html'

    def get_context_data(self, *args, **kwargs):
        context = super(TagSearchView, self).get_context_data(**kwargs)
        tag_list = kwargs.get('tag_list').split(',')

        # artist_list_all = Artist.objects.all()
        # dict_artist_and_count = {}
        #
        # for artist in artist_list_all:
        #     dict_artist_and_count.update({artist: 0})
        #
        # for tag in tag_list:
        #     artist_list = Artist.objects.filter(tags__name__in=[tag])
        #
        #     for artist in artist_list:
        #         count = dict_artist_and_count[artist]
        #         dict_artist_and_count[artist] = (count+1)
        #
        # sort_dict_artist_and_count = sorted(dict_artist_and_count.items(), key=lambda x: x[1], reverse=True)
        #
        # sort_dict_artist = []
        # sort_dict_count = []
        # for value in sort_dict_artist_and_count:
        #     sort_dict_artist.append(value[0])
        #     sort_dict_count.append(value[1])

        #　===================
        #
        # ユーザのフォローしている作者の作者タグを順位付け

        # すべての作者のリスト
        all_artist_list = Artist.objects.all()

        # 検索タグにヒットした作者のリスト
        for tag in tag_list:
            hit_tag_artist_list = Artist.objects.filter(tags__name__in=[tag])
        print(hit_tag_artist_list)

        # タグとタグ数の辞書
        dict_tag_and_count_list = {}

        # ユーザのフォローしている作者
        user_follow_artist_list = self.request.user.fav_artist.all()

        # ユーザのフォローしている作者すべてから、タグを抽出
        for artist in user_follow_artist_list:
            all_artist_tag = artist.tags.all()
            for tag in all_artist_tag:
                if tag in dict_tag_and_count_list.keys():
                    dict_tag_and_count_list[tag] += 1
                else:
                    dict_tag_and_count_list.update({tag: 1})

        # タグを多い順にソートして5つだけにした辞書（優先作者タグ）
        dict_sort_tag_list = sorted(dict_tag_and_count_list.items(), key=lambda x: x[1], reverse=True)
        dict_sort_tag_list_order = OrderedDict(sorted(dict_tag_and_count_list.items(), key=lambda x: x[1], reverse=True))

        # ソートされたタグのリスト（優先作者タグリスト）
        dict_sort_tag_list_order_keys = list(dict_sort_tag_list_order.keys())[:5]

        # 優先作者タグリストからリサーチ
        dict_artist_and_count_list = {}
        for tag in dict_sort_tag_list_order_keys:
            print(tag)
            # （優先作者タグ）&&（検索タグにヒットした作者のリスト）
            research_tag_artist_list = Artist.objects.filter(tags__name__in=[tag]) & hit_tag_artist_list
            for artist in research_tag_artist_list:
                if artist in dict_artist_and_count_list:
                    dict_artist_and_count_list[artist] += 1
                else:
                    dict_artist_and_count_list.update({artist: 1})

        # 作者を降順にリスト化
        dict_sort_artist_list_order = list(OrderedDict(sorted(dict_artist_and_count_list.items(),
                                                              key=lambda x: x[1], reverse=True)).keys())

        # フォローしていない作者リスト
        dict_sort_artist_list_order_non_follow = copy.deepcopy(dict_sort_artist_list_order)
        for artist in user_follow_artist_list:
            dict_sort_artist_list_order_non_follow.remove(artist)

        context['all_artist_list'] = all_artist_list
        context['hit_tag_artist_list'] = hit_tag_artist_list
        context['dict_sort_tag_list_order'] = list(dict_sort_tag_list)[:5]
        context['user_follow_artist_list'] = user_follow_artist_list
        context['dict_sort_artist_list_order'] = dict_sort_artist_list_order
        context['dict_sort_artist_list_order_non_follow'] = dict_sort_artist_list_order_non_follow
        return context


