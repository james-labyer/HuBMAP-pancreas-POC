import pandas as pd
from dash import Dash, dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import math

app = Dash(external_stylesheets=[dbc.themes.LUMEN])

LAYERS = ["All", "Layer 1", "Layer 2", "Layer 3", "Layer 4"]
X_AXIS = [221, 271, 321, 371, 421, 471, 521, 571, 621, 671]
Y_AXIS = [248, 301, 354, 407, 460, 513]
Z_AXIS = [0, 35, 70, 105, 140]
D_PROTEIN = "INS"
D_SCHEME = "Jet"

C_SCHEMES = [
    "bluered",
    "deep",
    "delta",
    "greys",
    "haline",
    "ice",
    "inferno",
    "jet",
    "magma",
    "plasma",
    "spectral",
    "thermal",
    "viridis",
    "ylgnbu",
    "ylorrd",
]

cubes_df1 = pd.read_csv("assets/rectangles_output.csv")
points_df = pd.read_csv("assets/HuBMAP_ili_data10-11-24.csv")
protein_df = pd.read_csv("assets/protein_labels.csv")
proteins = protein_df.columns.tolist()


def select_layer(zlayer, df):
    if zlayer == "All":
        return df
    elif zlayer == "Layer 1":
        return df[df["Z Center"] < 35]
    elif zlayer == "Layer 2":
        return df[(df["Z Center"] >= 35) & (df["Z Center"] < 70)]
    elif zlayer == "Layer 3":
        return df[(df["Z Center"] >= 70) & (df["Z Center"] < 105)]
    elif zlayer == "Layer 4":
        return df[df["Z Center"] >= 105]


def get_colors(df, protein):
    colors = [
        df[df["Y Center"] < 301].loc[:, protein].to_list(),
        df[(df["Y Center"] >= 301) & (df["Y Center"] < 354)].loc[:, protein].to_list(),
        df[(df["Y Center"] >= 354) & (df["Y Center"] < 407)].loc[:, protein].to_list(),
        df[(df["Y Center"] >= 407) & (df["Y Center"] < 460)].loc[:, protein].to_list(),
        df[df["Y Center"] >= 460].loc[:, protein].to_list(),
    ]
    return colors


def make_sphere(x, y, z, radius, resolution=20):
    """Return the coordinates for plotting a sphere centered at (x,y,z)"""
    u, v = np.mgrid[0 : 2 * np.pi : resolution * 2j, 0 : np.pi : resolution * 1j]
    X = radius * np.cos(u) * np.sin(v) + x
    Y = radius * np.sin(u) * np.sin(v) + y
    Z = radius * np.cos(v) + z
    return (X, Y, Z)


def make_fig1(
    opacity=0.4, caps=True, colorscheme=D_SCHEME, protein=D_PROTEIN, layer="All"
):
    df3 = select_layer(layer, cubes_df1)

    X = df3.loc[:, "X Center"]
    Y = df3.loc[:, "Y Center"]
    Z = df3.loc[:, "Z Center"]
    values = df3.loc[:, protein]

    fig1 = go.Figure(
        data=go.Volume(
            x=X,
            y=Y,
            z=Z,
            value=values,
            isomin=math.floor(protein_df.loc[0, protein]),
            isomax=math.ceil(protein_df.loc[1, protein]),
            opacity=opacity,
            surface_count=180,
            slices_z=dict(show=True, locations=[0.4]),
            caps=dict(x_show=caps, y_show=caps, z_show=caps, x_fill=1),
            colorscale=colorscheme,
        )
    )

    fig1.update_layout(
        scene=dict(
            xaxis=dict(tickvals=X_AXIS),
            yaxis=dict(tickvals=Y_AXIS),
            zaxis=dict(tickvals=Z_AXIS),
        )
    )
    return fig1


def make_fig2(opacity=0.1, colorscheme=D_SCHEME, protein=D_PROTEIN, layer="All"):
    df4 = select_layer(layer, points_df)
    X = df4.loc[:, "X Center"]
    Y = df4.loc[:, "Y Center"]
    Z = df4.loc[:, "Z Center"]
    values = df4.loc[:, protein]

    fig2 = go.Figure(
        data=go.Volume(
            x=X,
            y=Y,
            z=Z,
            value=values,
            isomin=math.floor(protein_df.loc[0, protein]),
            isomax=math.ceil(protein_df.loc[1, protein]),
            opacity=opacity,
            colorscale=colorscheme,
            surface_count=21,
        )
    )
    return fig2


def make_fig3(cscheme=D_SCHEME, protein=D_PROTEIN):
    x = X_AXIS[:9]
    y = Y_AXIS[:5]
    z1 = [[35 for i in x] for j in y]
    z2 = [[70 for i in x] for j in y]
    z3 = [[105 for i in x] for j in y]
    z4 = [[140 for i in x] for j in y]

    color_sets = []

    for k in range(4):
        this_layer = select_layer(LAYERS[k], points_df)
        color_sets.append(get_colors(this_layer, protein))

    fig = go.Figure(
        data=[
            go.Surface(x=x, y=y, z=z1, colorscale=cscheme, surfacecolor=color_sets[0]),
            go.Surface(
                x=x,
                y=y,
                z=z2,
                showscale=False,
                colorscale=cscheme,
                surfacecolor=color_sets[1],
            ),
            go.Surface(
                x=x,
                y=y,
                z=z3,
                showscale=False,
                colorscale=cscheme,
                surfacecolor=color_sets[2],
            ),
            go.Surface(
                x=x,
                y=y,
                z=z4,
                showscale=False,
                colorscale=cscheme,
                surfacecolor=color_sets[3],
            ),
        ]
    )

    return fig


def make_fig4(opacity=1, cscheme=D_SCHEME, protein=D_PROTEIN):
    res = 5
    data = []
    cmin = math.floor(protein_df.loc[0, protein])
    cmax = math.ceil(protein_df.loc[1, protein])
    for k in points_df.index:
        s_color = points_df.loc[k, protein]
        if not np.isnan(s_color):
            (X, Y, Z) = make_sphere(
                x=points_df.loc[k, "X Center"],
                y=points_df.loc[k, "Y Center"],
                z=points_df.loc[k, "Z Center"],
                radius=16,
                resolution=res,
            )
            c = [[s_color.item() for i in range(res)] for j in range(res * 2)]
            if k == 1:
                data.append(
                    go.Surface(
                        x=X,
                        y=Y,
                        z=Z,
                        surfacecolor=c,
                        colorscale=cscheme,
                        cmin=cmin,
                        cmax=cmax,
                        opacity=opacity,
                    )
                )
            else:
                data.append(
                    go.Surface(
                        x=X,
                        y=Y,
                        z=Z,
                        surfacecolor=c,
                        colorscale=cscheme,
                        cmin=cmin,
                        cmax=cmax,
                        showscale=False,
                        opacity=opacity,
                    )
                )

    fig4 = go.Figure(data=data)
    return fig4


app.layout = html.Div(
    children=[
        html.Header(
            children=[
                html.H1("Spatial Proteome Map of a Single Human Islet Microenvironment")
            ]
        ),
        html.Main(
            id="main-content",
            children=[
                html.Div(
                    id="navbar",
                    children=[
                        dbc.Nav(
                            [
                                dbc.NavLink(
                                    "Proteome Cross-Section View",
                                    href="#cross-section",
                                    external_link=True,
                                ),
                                dbc.NavLink(
                                    "Proteomics Scatter Plot",
                                    href="#scatter-plot",
                                    external_link=True,
                                ),
                                dbc.NavLink(
                                    "Download Data",
                                    href="#download-dataset",
                                    external_link=True,
                                ),
                            ],
                            vertical=True,
                        )
                    ],
                ),
                html.Div(
                    id="content-div",
                    children=[
                        html.Section(
                            id="cross-section",
                            children=[
                                html.Header(html.H2("Proteome Cross-Section View")),
                                html.P(
                                    "Here is a 3D cross-section of the tissue. Select a protein to view its concentrations throughout the tissue sample:"
                                ),
                                dcc.Dropdown(
                                    proteins,
                                    D_PROTEIN,
                                    id="proteinsdd",
                                ),
                                html.P("Select a tissue layer to view"),
                                dcc.Dropdown(
                                    LAYERS,
                                    "All",
                                    id="layersdd",
                                ),
                                dcc.Graph(
                                    figure=make_fig1(),
                                    className="dcc-graph",
                                    id="cross-section-graph",
                                ),
                                html.Div(
                                    children=[
                                        html.Div(
                                            id="caps-and-color-div",
                                            children=[
                                                html.Div(
                                                    children=[
                                                        html.P(
                                                            "Add or remove end caps:"
                                                        ),
                                                        dbc.Switch(
                                                            id="fig1capswitch",
                                                            value=False,
                                                        ),
                                                    ],
                                                    id="caps-div",
                                                ),
                                                html.Div(
                                                    children=[
                                                        html.P(
                                                            "Choose a color scheme:"
                                                        ),
                                                        dcc.Dropdown(
                                                            C_SCHEMES,
                                                            D_SCHEME,
                                                            id="fig1colorschemedd",
                                                        ),
                                                    ],
                                                    id="color-scheme-div",
                                                ),
                                            ],
                                        ),
                                        html.Div(
                                            children=[
                                                html.P(
                                                    "Adjust the opacity of the model:"
                                                ),
                                                dcc.Slider(
                                                    0,
                                                    1,
                                                    0.2,
                                                    value=0.4,
                                                    id="fig1opacityslider",
                                                ),
                                            ],
                                            id="opacity-div",
                                        ),
                                    ],
                                    id="cross-section-controls",
                                ),
                                html.Div(
                                    children=[
                                        dcc.Graph(
                                            figure=make_fig2(),
                                            className="dcc-graph",
                                            id="cross-section-graph2",
                                        ),
                                    ]
                                ),
                                html.Div(
                                    children=[
                                        html.Div(
                                            children=[
                                                html.P("Choose a color scheme:"),
                                                dcc.Dropdown(
                                                    C_SCHEMES,
                                                    D_SCHEME,
                                                    id="fig2colorschemedd",
                                                ),
                                            ],
                                            id="fig2-color-scheme-div",
                                        ),
                                        html.Div(
                                            children=[
                                                html.P(
                                                    "Adjust the opacity of the model:"
                                                ),
                                                dcc.Slider(
                                                    0,
                                                    1,
                                                    0.2,
                                                    value=0.4,
                                                    id="fig2opacityslider",
                                                ),
                                            ],
                                            id="fig2-opacity-div",
                                        ),
                                    ],
                                    id="fig2-cross-section-controls",
                                ),
                                html.Div(
                                    children=[
                                        dcc.Graph(
                                            figure=make_fig3(),
                                            className="dcc-graph",
                                            id="cross-section-graph3",
                                        ),
                                    ]
                                ),
                                html.Div(
                                    children=[
                                        html.P("Choose a color scheme:"),
                                        dcc.Dropdown(
                                            C_SCHEMES,
                                            D_SCHEME,
                                            id="fig3colorschemedd",
                                        ),
                                    ],
                                    id="fig3-color-scheme-div",
                                ),
                                html.Div(
                                    dcc.Graph(
                                        figure=make_fig4(),
                                        className="dcc-graph",
                                        id="cross-section-graph4",
                                    ),
                                ),
                                html.Div(
                                    children=[
                                        html.Div(
                                            children=[
                                                html.P("Choose a color scheme:"),
                                                dcc.Dropdown(
                                                    C_SCHEMES,
                                                    D_SCHEME,
                                                    id="fig4colorschemedd",
                                                ),
                                            ],
                                            id="fig4-color-scheme-div",
                                        ),
                                        html.Div(
                                            children=[
                                                html.P(
                                                    "Adjust the opacity of the model:"
                                                ),
                                                dcc.Slider(
                                                    0,
                                                    1,
                                                    0.2,
                                                    value=1,
                                                    id="fig4opacityslider",
                                                ),
                                            ],
                                            id="fig4-opacity-div",
                                        ),
                                    ],
                                    id="fig4-cross-section-controls",
                                ),
                            ],
                        ),
                        html.Section(
                            id="scatter-plot",
                            children=[
                                html.Header(html.H2("Proteomics Scatter Plot")),
                                html.P("Explanation text"),
                                html.Div(
                                    "Visualization placeholder",
                                    className="viz-placeholder",
                                ),
                            ],
                        ),
                        html.Section(
                            id="download-dataset",
                            children=[
                                html.Header(html.H2("Download Data Here")),
                                html.Div(
                                    children=[
                                        html.P(
                                            "Here is the data collected in this study, available as an Excel file or a VTK file."
                                        ),
                                        dbc.Button(
                                            "Download Excel Spreadsheet",
                                            id="btn-download-xlsx",
                                            className="download-button",
                                        ),
                                        dcc.Download(id="download-xlsx"),
                                        dbc.Button(
                                            "Download VTK File",
                                            id="btn-download-vtk",
                                            className="download-button",
                                        ),
                                        dcc.Download(id="download-vtk"),
                                    ]
                                ),
                                html.Hr(),
                                html.Div(
                                    children=[
                                        html.P(
                                            children=[
                                                "If you would like to visualize this data using the `ili spatial data mapping tool, open the ",
                                                html.A(
                                                    "`ili website",
                                                    href="http://ili.embl.de/",
                                                ),
                                                ", select 'Volume', and drag and drop the following two files into the viewer:",
                                            ]
                                        ),
                                    ]
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        html.Footer("This site made possible by the Texas Advanced Computing Center."),
    ]
)


@callback(
    Output("cross-section-graph", "figure"),
    Output("cross-section-graph2", "figure"),
    Output("cross-section-graph3", "figure"),
    Output("cross-section-graph4", "figure"),
    Input("fig1opacityslider", "value"),
    Input("fig1capswitch", "value"),
    Input("fig1colorschemedd", "value"),
    Input("fig2opacityslider", "value"),
    Input("fig2colorschemedd", "value"),
    Input("fig3colorschemedd", "value"),
    Input("fig4opacityslider", "value"),
    Input("fig4colorschemedd", "value"),
    Input("proteinsdd", "value"),
    Input("layersdd", "value"),
)
def update_output(
    fig1opacityslider,
    fig1capswitch,
    fig1colorschemedd,
    fig2opacityslider,
    fig2colorschemedd,
    fig3colorschemedd,
    fig4opacityslider,
    fig4colorschemedd,
    proteinsdd,
    layersdd,
):
    fig1 = make_fig1(
        fig1opacityslider, fig1capswitch, fig1colorschemedd, proteinsdd, layersdd
    )
    fig2 = make_fig2(fig2opacityslider, fig2colorschemedd, proteinsdd, layersdd)
    fig3 = make_fig3(fig3colorschemedd, protein=proteinsdd)
    fig4 = make_fig4(fig4opacityslider, fig4colorschemedd, proteinsdd)
    return fig1, fig2, fig3, fig4


@callback(
    Output("download-xlsx", "data"),
    Input("btn-download-xlsx", "n_clicks"),
    prevent_initial_call=True,
)
def download_xlsx(n_clicks):
    return dcc.send_file("assets/HubMAP_TMC_p1_20C_3D_protINT_May8_sorted.xlsx")


@callback(
    Output("download-vtk", "data"),
    Input("btn-download-vtk", "n_clicks"),
    prevent_initial_call=True,
)
def download_vtk(n_clicks):
    return dcc.send_file("assets/HubMAP_TMC_p1_20C_3D_protINT_May8_sorted.vti")


if __name__ == "__main__":
    app.run_server(debug=True)
