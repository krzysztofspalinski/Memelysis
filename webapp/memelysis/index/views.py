from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from django.shortcuts import render, redirect
from .models import Memes, MemesClusters, Sources
from .utils import get_distribution_plot
from django.views.generic import TemplateView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template.loader import render_to_string
from django.http import JsonResponse


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
    memes_dct = list(Memes.objects.values_list('id', 'url', 'image_path', 'source__name', 'memesupvotesstatistics__upvotes',
                                               'memesupvotesstatistics__upvotes_centile', 'memesclusters__cluster', 'meme_datetime'))
    df = pd.DataFrame(memes_dct)
    df.columns = ['id', 'url', 'image_path', 'source',
                  'upvotes', 'upvotes_centile', 'cluster', 'meme_datetime']

    pallete = ['#b2182b', '#ef8a62', '#999999', '#4d4d4d']
    # ======= FIG1
    df1 = df.groupby('source').size().reset_index()
    df1.columns = ['source', 'memes count']

    fig = px.pie(df1,
                 values='memes count',
                 names='source',
                 title='Source participation',
                 color_discrete_sequence=pallete)

    fig1_html = fig.to_html()
    # ========= FIG2
    df2 = df.groupby('cluster').size().reset_index()
    df2.columns = ['cluster', 'memes count']

    fig = px.pie(df2,
                 values='memes count',
                 names='cluster',
                 title='Cluster participation',
                 color_discrete_sequence=pallete)
    fig.update_layout(title="Cluster participation")
    fig2_html = fig.to_html()
    # ========== FIG3
    df['meme_date'] = df.meme_datetime.dt.date
    unique_days_of_scraping = len(df.meme_date.unique())

    df['meme_hour'] = df.meme_datetime.dt.hour.astype(int)
    df3 = df.groupby(['source', 'meme_date']).size().reset_index()
    df3.columns = ['source', 'meme_date', 'meme count']

    df3hour = df.groupby(['source', 'meme_hour']).size().reset_index()
    df3hour.columns = ['source', 'meme_hour', 'meme count']
    df3hour['avg meme count'] = df3hour['meme count'] / unique_days_of_scraping

    fig = px.line(df3, x="meme_date", y="meme count", color='source',
                  color_discrete_sequence=pallete, template='xgridoff')
    fig.update_layout(title="Number of memes collected by source",
                      xaxis_title="Date",
                      yaxis_title="Number of memes")
    fig3_html = fig.to_html()
    # ========= FIG4
    fig = px.line(df3hour, x="meme_hour", y="avg meme count", color='source',
                  color_discrete_sequence=pallete, template='xgridoff')
    fig.update_layout(title="Average daily number of memes collected by source",
                      xaxis_title="Hour",
                      yaxis_title="Number of memes")
    fig4_html = fig.to_html()
    # ========= FIG5
    df3_cumsum = df3.groupby(['source', 'meme_date']).sum().groupby(
        level=0).cumsum().reset_index()
    df3hour_cumsum = df3hour.groupby(['source', 'meme_hour']).sum().groupby(
        level=0).cumsum().reset_index()

    df3cluster = df.groupby(['cluster', 'meme_date']).size().reset_index()
    df3cluster.columns = ['cluster', 'meme_date', 'meme count']
    df3_cumsum_cluster = df3cluster.groupby(
        ['cluster', 'meme_date']).sum().groupby(level=0).cumsum().reset_index()

    fig = px.line(df3cluster, x="meme_date", y="meme count", color='cluster',
                  color_discrete_sequence=pallete)
    fig.update_layout(title="Average number of memes collected by cluster",
                      xaxis_title="Date",
                      yaxis_title="Number of memes")
    fig5_html = fig.to_html()
    # ========= FIG6
    fig = px.line(df3hour_cumsum, x="meme_hour", y="avg meme count", color='source',
                  color_discrete_sequence=pallete)
    fig.update_layout(title="Cumulative number of memes collected by source",
                      xaxis_title="Date",
                      yaxis_title="Number of memes")
    fig6_html = fig.to_html()
    # ========= FIG7
    fig = px.area(df3, x="meme_date", y="meme count",
                  color="source", color_discrete_sequence=pallete)
    fig.update_layout(title="Average number of memes collected by source",
                      xaxis_title="Date",
                      yaxis_title="Number of memes")
    fig7_html = fig.to_html()
    # ========== FIG8
    fig = px.area(df3_cumsum, x="meme_date", y="meme count",
                  color="source", color_discrete_sequence=pallete)
    fig.update_layout(title="Cumulative number of memes collected by source",
                      xaxis_title="Date",
                      yaxis_title="Number of memes")
    fig8_html = fig.to_html()
    # ========== FIG9
    df4 = df.groupby(['source', 'cluster']).size().reset_index()
    df4.columns = ['source', 'cluster', 'meme count']
    df4 = pd.pivot_table(df4, values='meme count', index=[
                         'source'], columns='cluster')
    # Nodes & links
    nodesIds = list(df4.index) + list(df4.columns)

    # nodes = [['ID', 'Label', 'Color'],
    #         [0,nodesIds[0],'#4994CE'],
    #         [1,nodesIds[1],'#449E9E'],
    #         [2,nodesIds[2],'#8A5988'],
    #         [3,nodesIds[3],'#7FC241']]

    nodes = [['ID', 'Label', 'Color']]

    colors = ['#7FC241', '#8A5988', '#449E9E', '#4994CE']
    names = ['memedroid', 'reddit', 'imgur', 'twitter']
    nodes = nodes + [[1 + i, name, pallete[i]]
                     for i, name in enumerate(list(df4.index))]
    nodes = nodes + [[4 + i, name, '#4d4d4d']
                     for i, name in enumerate(list(df4.columns))]
    #nodesIds = ['twitter', 'reddit', 'imgur', 'memedroid'] + list(df4.columns)

    links = [['Source', 'Target', 'Value', 'Link Color']]

    for source in list(df4.index):
        for cluster in list(df4.columns):
            if not np.isnan(df4.loc[source, cluster]):
                links.append([nodesIds.index(source), nodesIds.index(
                    cluster), df4.loc[source, cluster], 'rgba(211, 211, 211, 0.5)'])

    # Retrieve headers and build dataframes
    nodes_headers = nodes.pop(0)
    links_headers = links.pop(0)
    df_nodes = pd.DataFrame(nodes, columns=nodes_headers)
    df_links = pd.DataFrame(links, columns=links_headers)

    # Sankey plot setup
    data_trace = dict(
        type='sankey',
        domain=dict(
            x=[0, 1],
            y=[0, 1]
        ),
        orientation="h",
        valueformat=".0f",
        node=dict(
            pad=10,
            thickness=30,
            line=dict(
                color="black",
                width=0
            ),
            label=df_nodes['Label'].dropna(axis=0, how='any'),
            color=df_nodes['Color']
        ),
        link=dict(
            source=df_links['Source'].dropna(axis=0, how='any'),
            target=df_links['Target'].dropna(axis=0, how='any'),
            value=df_links['Value'].dropna(axis=0, how='any'),
            color=df_links['Link Color'].dropna(axis=0, how='any'),
        )
    )

    layout = dict(
        title="Sankey's diagram for clusters' source distribution",
        height=600,
        font=dict(
            size=13))

    fig = go.Figure(data=[data_trace], layout=layout)
    fig9_html = fig.to_html()
    # ========= FIG10
    df5 = df.loc[df.upvotes < 800, :]
    fig = go.Figure()
    for i, source in enumerate(list(df5.source.unique())):
        fig.add_trace(go.Histogram(x=df5.loc[df5.source == source, 'upvotes'],
                                   name=source,
                                   histnorm='probability density',
                                   marker_color=pallete[i]))

    # The two histograms are drawn on top of another
    fig.update_layout(barmode='stack',
                      title="Upvotes distribution by source",
                      yaxis_title="Percentage",
                      xaxis_title="Number of upvotes")
    fig10_html = fig.to_html()

    context = {'figures': [fig1_html, fig2_html, fig3_html,
                           fig4_html, fig5_html, fig6_html, fig7_html, fig8_html, fig9_html, fig10_html]}
    return render(request, 'index/analytics.html', context=context)
