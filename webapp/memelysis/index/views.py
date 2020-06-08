from django.shortcuts import render, redirect
from .models import Memes, MemesClusters, Sources
from .utils import get_distribution_plot
from django.views.generic import TemplateView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template.loader import render_to_string
from django.http import JsonResponse

import requests
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot


import plotly.offline as opy
import plotly.graph_objs as go
import numpy as np
import requests
import plotly
import pandas as pd

from plotly.colors import named_colorscales
import plotly.express as px
import plotly.io as pio
pio.templates


class Graph(TemplateView):
    template_name = 'graph.html'

    def get_context_data(self, fig, vertical_line_position, **kwargs):
        context = super(Graph, self).get_context_data(**kwargs)

        fig.update_layout(xaxis_type="log", height=280,
                          xaxis={'title': 'Number of upvotes',
                                 'fixedrange': True},
                          yaxis={'title': 'Number of memes in bin',
                                 'fixedrange': True},
                          legend=dict(x=0, y=1.2, orientation='h'),
                          showlegend=True, margin=go.layout.Margin(
                              l=0,
                              r=0,
                              b=0,
                              t=0))

        fig.add_shape(
            go.layout.Shape(type='line', xref='x', yref='paper',
                            x0=vertical_line_position, y0=0,
                            x1=vertical_line_position, y1=1,
                            line={'width': 5, 'color': 'red'})
        )

        fig.add_scatter(x=[None], y=[None], mode='markers',
                        marker=dict(size=10, color='red'), marker_symbol='square',
                        legendgroup='', showlegend=True, name='This meme score')

        div = opy.plot(fig, auto_open=False, output_type='div')

        context['graph'] = div
        return context


def index(request):

    sorting = request.session.get('sort', '-meme_datetime')
    page = request.GET.get('page', 1)

    all_memes = Memes.objects.all().order_by(sorting).values('id', 'image_path', 'source__name', 'meme_datetime', 'memesclusters__cluster',
                                                             'memesupvotesstatistics__upvotes', 'memesupvotesstatistics__upvotes_centile')

    category = request.session.get('category')
    if category:
        all_memes = all_memes.filter(memesclusters__cluster=category)

    source = request.session.get('source')
    if source:
        all_memes = all_memes.filter(source__name=source)

    min_vf = request.session.get('min_vf', 0)
    all_memes = all_memes.filter(
        memesupvotesstatistics__upvotes_centile__gte=min_vf)

    paginator = Paginator(all_memes, 15)

    try:
        memes = paginator.page(page)
    except PageNotAnInteger:
        memes = paginator.page(1)
    except EmptyPage:
        memes = paginator.page(paginator.num_pages)

    sorting_options = (
        ('-meme_datetime', 'Newest'),
        ('meme_datetime', 'Oldest'),
        ('-memesupvotesstatistics__upvotes_centile', 'Best'),
        ('memesupvotesstatistics__upvotes_centile', 'Worst'),
    )

    categories = ["Select category"] + \
        list(MemesClusters.objects.values_list(
            'cluster', flat=True).distinct())

    sources = ["Select source"] + \
        list(Sources.objects.values_list(
            'name', flat=True).distinct())

    context = {'memes': memes, 'sorting_options': sorting_options,
               'categories': categories, 'min_vf': min_vf * 100, 'sources': sources}
    return render(request, 'index/home.html', context=context)


def get_graph(request):
    if request.method == "POST":
        meme_id = request.POST.get('id').split('_')[1]
        meme = Memes.objects.get(id=meme_id)
        meme_score = meme.memesupvotesstatistics.upvotes
        meme_source = meme.source.name
        if meme_source == "reddit":
            response = requests.get(
                'https://storage.googleapis.com/images-and-logs/distributions/reddit_hist.json', stream=True)
            hist = response.raw.read().decode('utf8')
        elif meme_source == "twitter":
            response = requests.get(
                'https://storage.googleapis.com/images-and-logs/distributions/twitter_hist.json', stream=True)
            hist = response.raw.read().decode('utf8')
        elif meme_source == "memedroid":
            response = requests.get(
                'https://storage.googleapis.com/images-and-logs/distributions/memedroid_hist.json', stream=True)
            hist = response.raw.read().decode('utf8')
        elif meme_source == "imgur":
            response = requests.get(
                'https://storage.googleapis.com/images-and-logs/distributions/imgur_hist.json', stream=True)
            hist = response.raw.read().decode('utf8')
        fig = plotly.io.from_json(hist)
        g = Graph()
        graph = g.get_context_data(fig, meme_score)
        return JsonResponse(graph['graph'], safe=False)
    else:
        return JsonResponse()


def sort(request):
    if request.method == "POST":
        request.session['sort'] = request.POST.get('sort', '-meme_datetime')
    return redirect(request.META.get('HTTP_REFERER'))


def select_category(request):
    if request.method == "POST":
        category = request.POST.get('category', '')
        categories = list(MemesClusters.objects.values_list(
            'cluster', flat=True).distinct())
        if category in categories:
            request.session['category'] = category
        else:
            request.session.pop('category')
    return redirect(request.META.get('HTTP_REFERER'))


def select_source(request):
    if request.method == "POST":
        source = request.POST.get('source', '')
        sources = list(Sources.objects.values_list(
            'name', flat=True).distinct())
        if source in sources:
            request.session['source'] = source
        else:
            request.session.pop('source')
    return redirect(request.META.get('HTTP_REFERER'))


def select_min_vf(request):
    if request.method == "POST":
        min_vf = float(request.POST.get('min_vf', '')) / 100
        request.session['min_vf'] = min_vf
    return redirect(request.META.get('HTTP_REFERER'))


def about(request):
    return render(request, 'index/about.html')


def analytics(request):
    context = {'figures': ['fig1.html', 'fig2.html', 'fig3.html',
                           'fig4.html', 'fig5.html', 'fig6.html', 'fig7.html', 'fig8.html', 'fig9.html', 'fig10.html']}
    return render(request, 'index/analytics.html', context=context)
