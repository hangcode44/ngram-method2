import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = dash.Dash(__name__)
server = app.server

# Load data
try:
    df = pd.read_excel('all_results_500_final.xlsx')
    df2 = pd.read_excel('all_results_10000_epoch_final.xlsx')
    df3 = pd.read_excel('all_results_10000_final.xlsx')
    logging.info("Excel files loaded successfully.")
except Exception as e:
    logging.error(f"Error loading Excel files: {e}")

# Define layout with tabs
app.layout = html.Div([
    html.Div([
        html.Div([
            html.H3('N-gram Frequencies (METHOD 2) by Epoch'),
            html.Br(),
            html.P('Select the n-gram type'),
            dcc.Dropdown(
                        id='n-gram-type-dropdown1',
                        options=[{'label': t, 'value': t} for t in df['N-gram type'].unique()],
                        value=df['N-gram type'].unique()[0]),
            html.P('Select the subfolder'),
            dcc.Dropdown(
                id='subfolder-dropdown1',
                options=[{'label': s, 'value': s} for s in df['Subfolder'].unique()],
                value=df['Subfolder'].unique()[0]
            ),
            html.P('Select the words to plot'),
            dcc.Dropdown(
                id='words-dropdown1',
                options=[{'label': w, 'value': w} for w in []],
                value=[],
                multi=True
                    ),
            html.P('Type the words to plot (separated by commas)'),
            dcc.Input(
                id='input-words1',
                type='text',
                placeholder='Enter words to plot'
            ),
            html.Button('Plot', id='plot-button1', n_clicks=0),
            dcc.Graph(id='n-gram-frequencies1'),
            dcc.Store(id='filtered-data-store1')
        ], style={'width': '48%', 'display': 'inline-block', 'vertical-align': 'top', 'padding-right': '20px'}),
        
        html.Div([
            html.H3('N-gram Frequencies (METHOD 2) Over Time'),
            html.Br(),
            html.P('Select the n-gram type'),
            dcc.Dropdown(
                        id='n-gram-type-dropdown2',
                        options=[{'label': t, 'value': t} for t in df['N-gram type'].unique()],
                        value=df['N-gram type'].unique()[0]),
            html.P('Select the subfolder'),
            dcc.Dropdown(
                id='subfolder-dropdown2',
                options=[{'label': s, 'value': s} for s in df['Subfolder'].unique()],
                value=df['Subfolder'].unique()[0]
            ),
            html.P('Select the words to plot'),
            dcc.Dropdown(
                id='words-dropdown2',
                options=[{'label': w, 'value': w} for w in []],
                value=[],
                multi=True
                    ),
            html.P('Type the words to plot (separated by commas)'),
            dcc.Input(
                id='input-words2',
                type='text',
                placeholder='Enter words to plot'
            ),
            html.Button('Plot', id='plot-button2', n_clicks=0),
            dcc.Graph(id='n-gram-frequencies2'),
            dcc.Store(id='filtered-data-store2')
        ], style={'width': '48%', 'display': 'inline-block', 'vertical-align': 'top', 'padding-left': '20px'})
    ])
])

# Define the callback to update filtered data and word options
@app.callback(
    Output('filtered-data-store1', 'data'),
    [Input('n-gram-type-dropdown1', 'value'),
     Input('subfolder-dropdown1', 'value')]
)
def update_filtered_data(n_gram_type, subfolder):
    filtered_data = df[(df['N-gram type'] == n_gram_type) & (df['Subfolder'] == subfolder)]
    return filtered_data.to_json()

# Define the callback to update word dropdown options
@app.callback(
    Output('words-dropdown1', 'options'),
    [Input('filtered-data-store1', 'data')]
)
def update_word_options(filtered_data_json):
    filtered_data = pd.read_json(filtered_data_json)
    word_options = [{'label': w, 'value': w} for w in filtered_data['N-Gram'].unique()]
    return word_options

# Define the callback to update figure
@app.callback(
    Output('n-gram-frequencies1', 'figure'),
    [Input('plot-button1', 'n_clicks')],
    [State('n-gram-type-dropdown1', 'value'),
     State('subfolder-dropdown1', 'value'),
     State('filtered-data-store1', 'data'),
     State('words-dropdown1', 'value'),
     State('input-words1', 'value')]
)
def update_figure(n_clicks, n_gram_type, subfolder, filtered_data_json, selected_words, input_words):
    if n_clicks == 0:
        return {}
    grouped_data = df2.groupby(['N-Gram', 'Subfolder']).sum().reset_index()
    filtered_data = pd.read_json(filtered_data_json)

    if input_words:
        input_words_list = input_words.split(',')
        selected_words.extend([w.strip() for w in input_words_list])

    if selected_words:
        filtered_data = filtered_data[filtered_data['N-Gram'].isin(selected_words)]
   
    fig = go.Figure()

    for ngram in selected_words:
        ngram_data = grouped_data[grouped_data['N-Gram'] == ngram]
        fig.add_trace(go.Bar(x=ngram_data['Subfolder'], y=ngram_data['Frequency'], name=ngram))

    fig.update_layout(
        xaxis_title='Epoch',
        yaxis_title='Frequency',
        legend_title='N-Gram',
        xaxis=dict(
            tickmode='array',
            tickvals=grouped_data['Subfolder'].unique(),
            ticktext=grouped_data['Subfolder'].unique()
        ),
        barmode='group'
    )
    
    return fig

# Define the callback to update filtered data and word options
@app.callback(
    Output('filtered-data-store2', 'data'),
    [Input('n-gram-type-dropdown2', 'value'),
     Input('subfolder-dropdown2', 'value')]
)
def update_filtered_data(n_gram_type, subfolder):
    filtered_data = df[(df['N-gram type'] == n_gram_type) & (df['Subfolder'] == subfolder)]
    return filtered_data.to_json()

# Define the callback to update word dropdown options
@app.callback(
    Output('words-dropdown2', 'options'),
    [Input('filtered-data-store2', 'data')]
)
def update_word_options(filtered_data_json):
    filtered_data = pd.read_json(filtered_data_json)
    word_options = [{'label': w, 'value': w} for w in filtered_data['N-Gram'].unique()]
    return word_options

# Define the callback to update figure
@app.callback(
    Output('n-gram-frequencies2', 'figure'),
    [Input('plot-button2', 'n_clicks')],
    [State('n-gram-type-dropdown2', 'value'),
     State('subfolder-dropdown2', 'value'),
     State('filtered-data-store2', 'data'),
     State('words-dropdown2', 'value'),
     State('input-words2', 'value')]
)
def update_figure(n_clicks, n_gram_type, subfolder, filtered_data_json, selected_words, input_words):
    if n_clicks == 0:
        return {}
    grouped_data = df3.groupby(['N-Gram', 'Subfolder']).sum().reset_index()
    filtered_data = pd.read_json(filtered_data_json)

    if input_words:
        input_words_list = input_words.split(',')
        selected_words.extend([w.strip() for w in input_words_list])

    if selected_words:
        filtered_data = filtered_data[filtered_data['N-Gram'].isin(selected_words)]
   
    fig = go.Figure()

    for ngram in selected_words:
        ngram_data = grouped_data[grouped_data['N-Gram'] == ngram]
        fig.add_trace(go.Scatter(x=ngram_data['Subfolder'], y=ngram_data['Frequency'], mode='lines+markers', name=ngram, line=dict(shape='spline')))

    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Frequency',
        legend_title='N-Gram',
        xaxis=dict(
            tickmode='array',
            tickvals=grouped_data['Subfolder'].unique(),
            ticktext=grouped_data['Subfolder'].unique(),
            tickangle=30,
        ),
    )

    return fig

if __name__ == '__main__':
    app.run(debug=True)
