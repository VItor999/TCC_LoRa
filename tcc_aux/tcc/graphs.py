from tcc import functions as f
import os 
import json
import plotly.graph_objects as graph
from dash import dcc, html, Dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt

def plot_FILTER(selected_cr,selected_sf,selected_bw):
    filter = []
    filter = f.merge_list(filter,selected_cr)
    filter = f.merge_list(filter,selected_sf)
    filter = f.merge_list(filter,selected_bw)
    return filter


def web(json_file):
    # TODO organize 
    sim_paths =  os.getcwd()
    #all_sims = f.get_folders(sim_paths)
    #all_sims =sorted(all_sims)
    results_path = 'results'
    config_g = None
    with open(f'{sim_paths}/{json_file}', 'r') as config_file:
        config_g = json.load(config_file)
    assert config_g != None, print(f'ERROR, graph_cong.json file not found {config_g}')    
    all_sims = []
    for tab in config_g['tabs']:
        all_sims.append(tab['content']['Plots from folder'])
    #print(all_sims)
    colors = [
        '#FF0000',  # Red
        '#008000',  # Green
        '#0000FF',  # Blue
        '#FFFF00',  # Yellow
        '#800080',  # Purple
        '#00FFFF',  # Cyan
        '#FF00FF',  # Magenta
        '#00FF00',  # Lime
        '#808000',  # Olive
        '#008080',  # Teal
        '#FFA500',  # Orange
        '#A52A2A',  # Brown
        '#800000',  # Maroon
        '#FFC0CB',  # Pink
        '#FFD700',  # Gold
        '#008B8B',  # Dark Cyan
        '#B8860B',  # Dark Golden Rod
        '#32CD32',  # Lime Green
        '#FF1493',  # Deep Pink
        '#FF4500',  # Orange Red
        '#2E8B57',  # Sea Green
        '#DAA520',  # Golden Rod
        '#D2691E',  # Chocolate
        '#CD5C5C',  # Indian Red
        '#ADFF2F',  # Green Yellow
    ]

    tab_style = {'fontWeight': 'bold','display': 'inline-block', \
                'padding': '6px', 'minWidth': '100px', 'maxWidth': '150px'}

    # Placeholder options for the dropdowns
    options_CR = [{'label': str(i), 'value': f'_{i}_'} for i in range(0, 5)]
    options_SF = [{'label': str(i), 'value': f'_{i}_'} for i in range(7, 13)]
    options_BW = [{'label': str(i), 'value': f'_{i}'} for i in [125, 250]]

    # Create a JupyterDash application
    app = Dash(__name__)
    # Create the list of Tab objects based on the config
    tabs = [dcc.Tab(label='main',\
                    value=f'main',\
                    style=tab_style)]
    t = [dcc.Tab(label=tab_info['title'],\
                    value=f"tab-{i}",\
                    style=tab_style) \
                            for i, tab_info in enumerate(config_g['tabs'])if tab_info['title'] != 'main']
    tabs = f.merge_list(tabs,t)
    # Define the layout of the application
    app.layout = html.Div([
        dcc.Tabs(id="tabs", value='main', children=tabs),
        html.Div(id='tabs-content'),
        html.Button('Save Graph', id='save_btn', n_clicks=0),
        dbc.Toast(
            id="simple-toast",
            header="Graph Saved",
            is_open=False,
            dismissable=True,
            duration=4000,
            icon="danger",
            
        ),
        html.Div([
            "X-axis min:",
            dcc.Input(id='x-axis-min', type='number', value=-20),
            "X-axis max:",
            dcc.Input(id='x-axis-max', type='number', value=-6)
        ]),
        dcc.Dropdown(
                    id='dropdown-cr',
                    options=options_CR,
                    value=[options_CR[0]['value']],  # Default value
                    multi=True
                ),
                dcc.Dropdown(
                    id='dropdown-sf',
                    options=options_SF,
                    value=[options_SF[0]['value']],  # Default value
                    multi=True
                ),
                dcc.Dropdown(
                    id='dropdown-bw',
                    options=options_BW,
                    value=[options_BW[0]['value']],  # Default value
                    multi=True
                ),
            dcc.Graph(id='graph')
    ])


    def last_click(_static_click=[0],add = False):  # Default argument is a list containing a single element [0]
        if (add):
            _static_click[0] += 1
        return _static_click[0]

    def generate_list_content(content):
        list_items = []
        for key, value in content.items():
            if key == 'Plots from folder':
                list_items.append(html.H3(f'{key}: {value}'))
            else:    # For other keys, just create a list item with the key-value pair
                list_items.append(html.Li(f"{key}: {value}"))
        return list_items

    @app.callback(Output("simple-toast", "is_open"),
                     [Input('save_btn', 'n_clicks'),
                      Input('dropdown-cr', 'value'),
                      Input('dropdown-sf', 'value'),
                      Input('dropdown-bw', 'value'),
                      Input('x-axis-min', 'value'),
                      Input('x-axis-max', 'value'),
                      Input('tabs', 'value')],
                     prevent_initial_call=True)
    def save_graph(n_clicks,selected_cr, selected_sf, selected_bw , xmin, xmax, tab):
        #clks = clicks(add=True)
        #print(f'{n_clicks}> {last_click()}')
        if n_clicks > last_click():
            last_click(add=True)
            filter = plot_FILTER(selected_cr, selected_sf, selected_bw) 
            plts = load_common_plts(tab,filter)
            save_path = './teste'
            #if (tab != 'main' ):
            if len(plts['keys']) > 0:
                fig, axs = plt.subplots(1, 2, figsize=(15, 5))
                f.create_dir('./figures')
                save_path = './figures/img_'
                name = ''
                for key in plts['keys']:
                    label = ' '.join(key.split('_')[0:-1])
                    #print(label)
                    name += label
                    axs[0].plot(plts['BER'][key]['X'], plts['BER'][key]['Y'], label= label)
                    axs[0].set_title('BER x SNR')
                    axs[0].set_xlabel('SNR (dB)')
                    axs[0].set_ylabel('BER')
                    axs[0].set_yscale('log')
                    axs[0].grid(True)
                    axs[1].plot(plts['MER'][key]['X'],plts['MER'][key]['Y'], label= label)
                    axs[1].set_title('MER x SNR')
                    axs[1].set_xlabel('SNR (dB)')
                    axs[1].set_ylabel('MER')
                    axs[1].set_yscale('log')
                    axs[1].grid(True)
                   
                for axis in axs:
                    axis.grid(True, which='both', linestyle='--', linewidth=0.5)
                    axis.set_xlim(xmin, xmax)
                    axis.set_ylim(10e-4,1.5)
                    axis.legend()
                plt.tight_layout()
            if (save_path != None):
                file = f'{save_path}{name.replace(" ","_")}.png'
                f.delete_file(file)
                plt.savefig(file, dpi=300, bbox_inches='tight', format='png')   
            plt.close('all')   
            return True
        else:
            return False
   
    def load_common_plts(tab,filter):
        plots_SNRxBER = dict()
        plots_SNRxMER = dict()
        keys = set()
        output = dict()
        for i in range(len(all_sims)): 
            if(tab != 'main'):
                if (tab == f'tab-{i}'):
                    snr_path = f'{all_sims[i]}/{results_path}/snr'  
                    ber_path = f'{all_sims[i]}/{results_path}/ber'
                    mer_path = f'{all_sims[i]}/{results_path}/mer'
                    plots_SNRxBER = f.load_data_for_plot(snr_path,ber_path,filter)
                    plots_SNRxMER = f.load_data_for_plot(snr_path,mer_path,filter)
                    keys = plots_SNRxBER.keys() & plots_SNRxMER.keys()
                    output = {'keys' : keys , 'BER' : plots_SNRxBER, 'MER' : plots_SNRxMER}
            else:    
                aux = all_sims[i]
                if type(aux) is list:
                    i = 0
                    for path in aux:
                        #
                        snr_path = f'{path}/{results_path}/snr'  
                        ber_path = f'{path}/{results_path}/ber'
                        mer_path = f'{path}/{results_path}/mer'
                        paux_SNRxBER = f.load_data_for_plot(snr_path,ber_path,filter)
                        paux_SNRxMER = f.load_data_for_plot(snr_path,mer_path,filter)
                        for key in paux_SNRxBER.keys():
                            plots_SNRxBER[f'{key}_sim{i}'] = paux_SNRxBER[key]
                        for key in paux_SNRxMER.keys():
                            plots_SNRxMER[f'{key}_sim{i}'] = paux_SNRxMER[key]
                       
                        local_keys = plots_SNRxBER.keys() & plots_SNRxMER.keys()
                        keys = keys.union(local_keys)
                        
                        i+=1
                    output = {'keys' : keys , 'BER' : plots_SNRxBER, 'MER' : plots_SNRxMER}
        return output
            

    @app.callback(Output('tabs-content', 'children'),
                Input('tabs', 'value'))
    def render_content(tab_value):
        if tab_value == 'main': return
        # Extract the index of the selected tab
        selected_index = int(tab_value.split('-')[1])
        # Get the content for the selected tab
        content = config_g['tabs'][selected_index]['content']
        return html.Div([
                html.Ul(children=generate_list_content(content)),
            #dcc.Graph(id='graph')
            ])


    # Define the callback to update the graph based on dropdown selections
    @app.callback(
        Output('graph', 'figure'),
        [Input('dropdown-cr', 'value'),
        Input('dropdown-sf', 'value'),
        Input('dropdown-bw', 'value'),
        Input('x-axis-min', 'value'),
        Input('x-axis-max', 'value'),
        Input('tabs', 'value')],
        prevent_initial_call=True
    )
    def update_graph(selected_cr, selected_sf, selected_bw , xmin, xmax, tab):
        
        filter = plot_FILTER(selected_cr, selected_sf, selected_bw)
        snr_path = ''
        ber_path = ''
        mer_path = ''
        #print(tab)
        fig = make_subplots(rows=1, cols=2,subplot_titles=('BER x SNR', 'MER x SNR'))
        len_colors = len(colors)
        #print(tab)
        plts = load_common_plts(tab,filter)
        i = 0
        #if (tab != 'main'):
        if len(plts['keys']) > 0:
            for key in plts['keys']:
                color = colors[i%len_colors]
                #difference = [a - b for a, b in zip(plots_SNRxBER[key]['Y'], plots_SNRxMER[key]['Y'])]

                #print(difference)  # Output: [9, 18, 27, 36]
                #input()
                #print(plts['BER'][key])
                fig.add_trace(graph.Scatter(x=plts['BER'][key]['X'], y=plts['BER'][key]['Y'], mode='lines', line=dict(color=color), name=f'{key}', legendgroup=key),row=1, col=1)
                fig.add_trace(graph.Scatter(x=plts['MER'][key]['X'], y=plts['MER'][key]['Y'], mode='lines', line=dict(color=color), name=f'{key}',legendgroup=key, showlegend=False),row=1, col=2)
                i+=1

        # Set the plot layout
        fig.update_layout(
            # ALL PLOTS
            autosize=False,
            width=1500,  
            height=550,
            title='Resultados da Simulação',
            # PLOT 1 
            xaxis=dict(
                title='SNR (dB)',
                range=[xmin, xmax]
            ),
            yaxis=dict(
                title='BER',
                type='log',
                exponentformat='e',
                showexponent='all'
            ),
            # PLOT 2
            xaxis2=dict(
                title='SNR (dB)',
                range=[xmin, xmax]
            ),
            yaxis2=dict(
                title='MER',
                type='log',
                exponentformat='e',
                showexponent='all'
            )
        )
        return fig
    
    app.run_server(debug=True)
if __name__ == '__main__':
    web()
