from django.shortcuts import render
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponseNotFound, HttpResponse
from datetime import datetime, timezone
from index.models import Memes, Sources, MemesUpvotesStatistics, MemesClusters
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.db.utils import IntegrityError
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


@csrf_exempt
def memes(request):
	if request.method == "POST":
		data = request.POST
		data_password = data.get('password', '')
		if str(data_password) == "82034723402347":
			try:
				meme_id_posted = data['id']
				url_posted = data['url']
				image_path_posted = data['image_path']
				source_posted = data['source']
				meme_timestamp_posted = data['meme_timestamp']
			except KeyError as e:
				return JsonResponse({'error': str(e)})
			else:
				meme_id = str(meme_id_posted)
				url = str(url_posted)
				image_path = str(image_path_posted)
				source, _ = Sources.objects.get_or_create(name=source_posted)
				print(meme_timestamp_posted)
				meme_datetime = datetime.fromtimestamp(
					int(meme_timestamp_posted), tz=timezone.utc)
				try:
					meme = Memes.objects.create(
						meme_id=meme_id,
						url=url,
						image_path=image_path,
						source=source,
						meme_datetime=meme_datetime
					)
					return JsonResponse(serializers.serialize('json', [meme]), safe=False)
				except IntegrityError as e:
					return JsonResponse({'error': str(e)})
		else:
			return JsonResponse({'error': 'Wrong password.'})
	else:
		return JsonResponse({'error': f"This request method is not supported: {request.method}"})


@csrf_exempt
def memes_scores(request):
	if request.method == "POST":
		data = request.POST
		data_password = data.get('password', '')
		if str(data_password) == "82034723402347":
			try:
				meme_id_posted = data['id']
				upvotes_posted = data['upvotes']
				upvotes_centile_posted = data['upvotes_centile']
			except KeyError as e:
				return JsonResponse({'error': str(e)})
			else:
				meme_id = str(meme_id_posted)
				upvotes = int(upvotes_posted)
				upvotes_centile = float(upvotes_centile_posted)
				try:
					meme = Memes.objects.get(meme_id=meme_id)
					meme_score = MemesUpvotesStatistics.objects.create(
						meme=meme,
						upvotes=upvotes,
						upvotes_centile=upvotes_centile,
					)
					return JsonResponse(serializers.serialize('json', [meme_score]), safe=False)
				except (IntegrityError, Memes.DoesNotExist) as e:
					return JsonResponse({'error': str(e)})
		else:
			return JsonResponse({'error': 'Wrong password.'})
	else:
		return JsonResponse({'error': f"This request method is not supported: {request.method}"})


@csrf_exempt
def memes_clusters(request):
	if request.method == "POST":
		data = request.POST
		data_password = data.get('password', '')
		if str(data_password) == "82034723402347":
			try:
				meme_id_posted = data['id']
				meme_cluster_posted = data['cluster']
			except KeyError as e:
				return JsonResponse({'error': str(e)})
			else:
				meme_id = str(meme_id_posted)
				meme_cluster = str(meme_cluster_posted)
				try:
					meme = Memes.objects.get(meme_id=meme_id)
					meme_cluster_object = MemesClusters.objects.create(
						meme=meme,
						cluster=meme_cluster,
					)
					return JsonResponse(serializers.serialize('json', [meme_cluster_object]), safe=False)
				except (IntegrityError, Memes.DoesNotExist) as e:
					return JsonResponse({'error': str(e)})
		else:
			return JsonResponse({'error': 'Wrong password.'})
	else:
		return JsonResponse({'error': f"This request method is not supported: {request.method}"})


def create_analytics_plots(request):
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
	df3hour['avg meme count'] = df3hour['meme count'] / \
		unique_days_of_scraping

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
	# nodesIds = ['twitter', 'reddit', 'imgur', 'memedroid'] + list(df4.columns)

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

	for i, fig_html in enumerate([fig1_html, fig2_html, fig3_html, fig4_html, fig5_html, fig6_html, fig7_html, fig8_html, fig9_html, fig10_html], 1):
		with open(f'index/templates/index/fig{i}.html', 'w') as f:
			f.write(fig_html)

	return HttpResponse()