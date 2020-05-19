from django.shortcuts import render
from .models import Memes
from .utils import get_distribution_plot
from django.views.generic import TemplateView
from django.core.paginator import Paginator


import plotly.offline as opy
import plotly.graph_objs as go
import numpy as np
import requests
import plotly

class Graph(TemplateView):
	template_name = 'graph.html'

	def get_context_data(self, fig, vertical_line_position, **kwargs):
		context = super(Graph, self).get_context_data(**kwargs)

		fig.update_layout(xaxis_type="log", height=280,
                  xaxis={'title': 'Number of upvotes','fixedrange':True},
                  yaxis={'title': 'Number of memes in bin','fixedrange':True},
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
							line={'width': 5, 'color':'red'})
		)

		fig.add_scatter(x=[None], y=[None], mode='markers',
			marker=dict(size=10, color='red'), marker_symbol='square',
			legendgroup='', showlegend=True, name='This meme score')

		div = opy.plot(fig, auto_open=False, output_type='div')

		context['graph'] = div
		return context






def index(request):



	response = requests.get('https://storage.googleapis.com/images-and-logs/distributions/reddit_hist.json', stream=True)
	reddit_hist = response.raw.read().decode('utf8')
	response = requests.get('https://storage.googleapis.com/images-and-logs/distributions/twitter_hist.json', stream=True)
	twitter_hist = response.raw.read().decode('utf8')
	response = requests.get('https://storage.googleapis.com/images-and-logs/distributions/memedroid_hist.json', stream=True)
	memedroid_hist = response.raw.read().decode('utf8')
	response = requests.get('https://storage.googleapis.com/images-and-logs/distributions/imgur_hist.json', stream=True)
	imgur_hist = response.raw.read().decode('utf8')



	page = request.GET.get('page', 1)

	all_memes = Memes.objects.all().order_by('-meme_datetime')

	paginator = Paginator(all_memes, 5)

	try:
		memes = paginator.page(page)
	except PageNotAnInteger:
		memes = paginator.page(1)
	except EmptyPage:
		memes = paginator.page(paginator.num_pages)

	graphs = []

	for meme in memes:
		meme_score = meme.memesupvotesstatistics.upvotes
		meme_source = meme.source.name

		if meme_source == 'reddit':
			fig = plotly.io.from_json(reddit_hist)
		if meme_source == 'twitter':
			fig = plotly.io.from_json(twitter_hist)
		if meme_source == 'memedroid':
			fig = plotly.io.from_json(memedroid_hist)
		if meme_source == 'imgur':
			fig = plotly.io.from_json(imgur_hist)
		g = Graph()
		graph = g.get_context_data(fig, meme_score)
		graphs.append(graph['graph'])
	
	context = {'data': zip(memes, graphs), 'memes': memes}
	return render(request, 'index/home.html', context=context)


def about(request):
	return render(request, 'index/about.html')


def analytics(request):
	return render(request, 'index/analytics.html')
