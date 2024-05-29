import dash
from dash import html, dcc, Input, Output, callback, State, dash_table
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Load data
products_df = pd.read_csv('data/products.csv')
vendors_df = pd.read_csv('data/vendors.csv')
reviews_df = pd.read_csv('data/reviews.csv')
products_cleaned_df = pd.read_csv('data/product_vendor.csv')
combined_data = pd.merge(products_cleaned_df, reviews_df, on='vendor', how='inner')
combined_data = combined_data[combined_data['name'] == combined_data['product']]
reviews_summary = combined_data.groupby(['main_business', 'rating']).size().unstack(fill_value=0)
products_df = products_cleaned_df


# Calculate statistics
total_products_markets = len(products_df)
total_vendors = len(vendors_df)
total_reviews = len(reviews_df)


# Setup for graph colors
graph_colors = {
    'background': '#121212',
    'text': '#7FDBFF'
}
#df = pd.DataFrame(data)
df = pd.read_csv('data/products_grouped.csv')

# Calculate the percentage share of each subcategory
total_products = df['product_count'].sum()
df['Percentage'] = (df['product_count'] / total_products * 100).round(2)

data_main_business = {
    'main_business': ['Data', 'Drug', 'Other'],
    'Count': [62, 193, 11]
}
df_main_business = pd.DataFrame(data_main_business)

data_side = {
    'Main Business': ['Data', 'Drug'],
    'Side Business Count': [14, 14],
    'Percentage': [22.6, 7.3]
}
df_side_business = pd.DataFrame(data_side)

category_descriptions = {
    'Data': 'Data-related products focusing on digital commodities like accounts, hacking tools, and information products.',
    'Drugs': 'Products related to recreational and pharmaceutical drugs, including both natural and synthetic substances.',
    'Digital Commerce': 'Counterfeit Items, Fraud, Services – These categories include fake goods, fraudulent schemes, and various services.',
    'Digital Security': 'Hacking and Cybersecurity, Software & Hosting – Involves products related to securing or breaching digital systems.',
    'Digital Knowledge Products': 'E-Books, Guides & Tutorials – Digital goods focused on information and educational content.',
    'Recreational Drugs': 'Cannabis & Hash, Psychedelics, Stimulants, Ecstasy, Dissociatives – Substances used primarily for recreational purposes.',
    'Pharmaceutical Drugs': 'Benzos, Opioids, Prescriptions, Steroids – Legally manufactured substances that are often used or distributed without medical supervision.',
    'Other Digital Products': 'Accounts, Others – Includes digital products like online account credentials and other miscellaneous digital goods.'
}

# Function to create logarithmic marks for the slider
def create_log_marks(start, end):
    log_start = np.log10(start)
    log_end = np.log10(end)
    marks = {i: f'${int(10**i)}' for i in np.arange(log_start, log_end + 0.1, 0.5)}
    return marks

def create_log_marks_vendor(start, end):
    log_start = np.log10(start)
    log_end = np.log10(end)
    marks = {i: f'{int(10**i)}' for i in np.arange(log_start, log_end + 0.1, 0.5)}
    return marks

log_min_price = np.log10(products_df['price_usd'].min())
log_max_price = np.log10(products_df['price_usd'].max())


# Initialize the Dash app
app = dash.Dash(__name__)

server = app.server

app.layout = html.Div([
   # html.H1("Dark Web Data Markets Analysis"),
    dcc.Tabs([
        dcc.Tab(label='Overview', children=[
            html.Div([
                html.Div([
                    html.H1("Exploration of Dark Web Data Markets", style={'textAlign': 'center'}),
                ], className='text-card'),
                html.Div([
                    html.P(
                        "This interactive platform is designed to delve into the evolving landscape of online dark markets, "
                        "highlighting the shift from traditional drug sales to the increasing prevalence of digital goods. "
                        "Through comprehensive data from the Nexus and WeTheNorth markets, this dashboard aims to elucidate "
                        "the differences in market dynamics between vendors dealing in physical goods, such as narcotics, "
                        "and those trading in digital commodities like credit card details, personal information, and leaked databases.",
                        style={'textAlign': 'center'}
                    ),
                ], className='text-card'),
                html.Div([
                    html.H3("Data Overview", style={'textAlign': 'center'}),
                    html.P(
                        "Data was scraped from two major dark web markets, Nexus and WeTheNorth. It includes detailed "
                        "listings of products, vendor profiles, and customer reviews.",
                        style={'textAlign': 'justify'}
                    ),
                    html.Div([
                        html.Div([
                            html.H4("Total Products", style={'color': '#007BFF'}),
                            html.P(f"{total_products_markets}", className='stats-number')  # Example static number
                        ], className='data-card'),
                        html.Div([
                            html.H4("Total Vendors", style={'color': '#28A745'}),
                            html.P(f"{total_vendors}", className='stats-number')  # Example static number
                        ], className='data-card'),
                        html.Div([
                            html.H4("Total Reviews", style={'color': '#DC3545'}),
                            html.P(f"{total_reviews}", className='stats-number')  # Example static number
                        ], className='data-card')
                    ], style={'display': 'flex', 'justifyContent': 'space-around'}),
                ], className='text-card'),
                html.Div([
                    html.H3("Key Insights", style={'textAlign': 'center'}),
                    html.Ul([
                        html.Li("Data related products constitute a significant proportion of all listings."),
                        html.Li("Physical goods vendors typically have higher review counts.")
                    ]),
                ], className='text-card'),
                html.Div([
                    html.H3("Guide", style={'textAlign': 'center'}),
                    html.P(
                        "Use the tabs to navigate between different views of the data. Each tab focuses on a different aspect "
                        "of the market, from overall trends to individual vendor activities. Hover over charts and elements or click for "
                        "more information or to drill down into specific data points.",
                        style={'textAlign': 'justify'}
                    ),
                ], className='text-card'),
            ], style={'padding': '40px 200px',
                      'backgroundColor': '#333',
                      })
        ]),
        dcc.Tab(label='Products', children=[
            dcc.Store(id='current-selection', storage_type='memory'),
            html.Div([
                dcc.Graph(
                    id='product-treemap',
                    figure=px.treemap(df, path=['main_business', 'category'], values='product_count',
                                      title='Product Category Distribution').update_layout(
                        plot_bgcolor=graph_colors['background'],
                        paper_bgcolor=graph_colors['background'],
                        font_color=graph_colors['text']
                    ),
                    config={"responsive": True},
                    style={'width': '70%', 'height': '500px'}  # Adjust width and height to make the treemap bigger
                ),
                html.Div(id='data-card', className='data-card', style={
                    'width': '30%',  # Adjust width to 30%
                    'display': 'flex',
                    'flexDirection': 'column',
                    'justifyContent': 'center',  # Vertically center the content in the data card
                    'alignItems': 'center',  # Horizontally center the content in the data card
                    'height': '150px',  # Match height to treemap for alignment
                    'padding': '20px',
                    'margin-top': '175px',
                    'margin-right': '75px',
                })
            ], style={
                'display': 'flex',
                'flexDirection': 'row',
                'alignItems': 'stretch',  # This will make all child divs align their heights together
                'justifyContent': 'space-between',
                'width': '100%',
                'height': '100%'
                # You might need to adjust this if you have other components above or below this layout
            }),
            html.Div([
                dcc.Graph(id='subcategory-pie'),
                dcc.Graph(id='price-range-bar')
            ], style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'space-between', 'padding': '0 75px'}),
            html.H3("Data Sample", style={'textAlign': 'left'}),
            html.Div([
                html.Label('Broad Category'),
                dcc.Dropdown(
                    id='broad-category-dropdown',
                    options=[{'label': category, 'value': category} for category in
                             products_df['broad_category'].unique()],
                    value=None,
                    placeholder="Select a broad category",
                    style={'color': 'black'}
                ),
                html.Label('Price Range'),
                dcc.RangeSlider(
                    id='price-range-slider',
                    min=log_min_price,
                    max=log_max_price,
                    step=0.1,
                    value=[log_min_price, log_max_price],
                    marks=create_log_marks(products_df['price_usd'].min(), products_df['price_usd'].max())
                )
            ], style={'padding': '20px'}),
            html.Div(id='table-container')
        ]),
        dcc.Tab(label='Vendors', children=[
            html.Div([
                html.Img(
                    src=app.get_asset_url('vendor_activity.png'),
                    style={'width': '60%', 'padding': '20px'}
                ),
                html.Div([
                    # Top row of data cards
                    html.Div([
                        html.Div([
                            html.H3('Total Data Vendors'),
                            html.P('Total vendors primarily dealing with data-related products: 157')
                        ], className='data-card'),
                        html.Div([
                            html.H3('Total Drug Vendors'),
                            html.P('Total vendors primarily dealing with drug-related products: 355')
                        ], className='data-card')
                    ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'}),
                    # Bottom row of data cards
                    html.Div([
                        html.Div([
                            html.H3('Percentage Data Side Business'),
                            html.P('Percentage of data-related vendors with a side business in drugs: 43.95%')
                        ], className='data-card'),
                        html.Div([
                            html.H3('Percentage Drug Side Business'),
                            html.P('Percentage of drug-related vendors with a side business in data: 19.44%')
                        ], className='data-card')
                    ], style={'display': 'flex', 'justifyContent': 'space-around'})
                ], style={
                    'width': '40%',  # Adjust width to 40% to give more space to cards
                    'display': 'flex',
                    'flexDirection': 'column',
                    'justifyContent': 'center',  # Center align the cards vertically
                    'alignItems': 'center',  # Center align the cards horizontally
                    'margin-top': '-160px'
                })
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}),
            dcc.Graph(
                id='review-summary-bar',
                figure=px.bar(reviews_summary, barmode='group',
                 title='Number of Positive and Negative Reviews by Product Category',
                 labels={'value': 'Number of Reviews', 'variable': 'Review Sentiment'},
                 color_discrete_map={'Positive': 'green', 'Negative': 'red'}).update_layout(
                    xaxis_title='Product Category',
                    yaxis_title='Number of Reviews',
                    legend_title='Review Sentiment',
                    plot_bgcolor='#333',  # Dark background
                    paper_bgcolor='#333',  # Dark background
                    font_color='white',  # White text
                )
            ),
            html.H3("Data Sample", style={'textAlign': 'left'}),
            html.Div([
                html.Label('Marketplace'),
                dcc.Dropdown(
                    id='marketplace-dropdown',
                    options=[{'label': category, 'value': category} for category in
                             vendors_df['marketplace'].unique()],
                    value=None,
                    placeholder="Select a broad category",
                    style={'color': 'black'}
                ),
                html.Label('Review Count Range'),
                dcc.RangeSlider(
                    id='review-range-slider',
                    min=log_min_price,
                    max=log_max_price,
                    step=0.1,
                    value=[log_min_price, log_max_price],
                    marks=create_log_marks_vendor(vendors_df['review_count'].min() + 1, vendors_df['review_count'].max())
                )
            ], style={'padding': '20px'}),
            html.Div(id='table-container-vendor')
        ])
    ])
])

def apply_layout_options(fig, layout_options):
    default_layout = {
        'plot_bgcolor': graph_colors['background'],
        'paper_bgcolor': graph_colors['background'],
        'font_color': graph_colors['text'],
        'barmode': 'group'
    }
    # Update with additional specific layout options
    fig.update_layout({**default_layout, **layout_options})
    return fig

@app.callback(
    Output('table-container', 'children'),
    [
        Input('broad-category-dropdown', 'value'),
        Input('price-range-slider', 'value')
    ]
)
def update_table(broad_category, price_range):
    filtered_df = products_df
    if broad_category:
        filtered_df = filtered_df[filtered_df['broad_category'] == broad_category]
    if price_range:
        min_price = 10 ** price_range[0]
        max_price = 10 ** price_range[1]
        filtered_df = filtered_df[(filtered_df['price_usd'] >= min_price) & (filtered_df['price_usd'] <= max_price)]

    filtered_df = filtered_df.head(10)

    return dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in filtered_df.columns],
        data=filtered_df.to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white'},
        style_cell={'backgroundColor': 'rgb(50, 50, 50)', 'color': 'white'},
    )

@app.callback(
    Output('table-container-vendor', 'children'),
    [
        Input('marketplace-dropdown', 'value'),
        Input('review-range-slider', 'value')
    ]
)
def update_table_vendor(marketplace, review_range):
    filtered_df = vendors_df
    if marketplace:
        filtered_df = filtered_df[filtered_df['marketplace'] == marketplace]
    if review_range:
        min_review = 10 ** review_range[0]
        max_review = 10 ** review_range[1]
        filtered_df = filtered_df[(filtered_df['review_count'] >= min_review) & (filtered_df['review_count'] <= max_review)]
    filtered_df = filtered_df[['name', 'about_text', 'review_count', 'marketplace']]
    filtered_df = filtered_df.head(10)

    return dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in filtered_df.columns],
        data=filtered_df.to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white'},
        style_cell={'backgroundColor': 'rgb(50, 50, 50)', 'color': 'white', 'maxWidth': '200px'},

    )

@app.callback(
    Output('review-summary-bar', 'figure'),
    [Input('review-summary-bar', 'clickData')],
    [State('review-summary-bar', 'figure')]
)
def toggle_review_visibility(clickData, current_figure):
    if clickData:
        # Determine which trace was clicked
        trace_index = clickData['points'][0]['curveNumber']
        # Load the current figure from JSON
        fig = go.Figure(current_figure)
        # Toggle visibility based on the click
        for i, trace in enumerate(fig.data):
            trace.visible = (i == trace_index)
        return fig
    else:
        return dash.no_update

# Callback to update the store based on treemap clicks
@app.callback(
    Output('current-selection', 'data'),
    [Input('product-treemap', 'clickData')],
    [State('current-selection', 'data')]
)
def update_selection_store(clickData, current_data):
    if not clickData:
        return None  # Reset when there's no data
    path = clickData['points'][0]['id'].split('/') if 'points' in clickData and 'id' in clickData['points'][0] else None
    return path


@app.callback(
    Output('data-card', 'children'),
    [Input('current-selection', 'data')]
)
def update_data_card(current_data):
    if not current_data:
        return html.Div([
            html.H4("Click a category to see details", style={'textAlign': 'center', 'color': 'white'}),
            html.P("Overview of product categories will be shown here.", style={'textAlign': 'center', 'color': 'white'})
        ])

    category = current_data[0]
    description = category_descriptions.get(category, "No specific information available for this category.")

    if len(current_data) == 1:
        # Main category
        return html.Div([
            html.H4(f"{category} Category", style={'textAlign': 'center', 'color': 'white'}),
            html.P(description, style={'textAlign': 'center', 'color': 'white'})
        ])
    elif len(current_data) == 2:
        # Subcategory
        subcategory = current_data[1]
        sub_description = category_descriptions.get(subcategory, "No specific information available for this subcategory.")
        return html.Div([
            html.H4(f"{subcategory} in {category}", style={'textAlign': 'center', 'color': 'white'}),
            html.P(sub_description, style={'textAlign': 'center', 'color': 'white'})
        ])

    return html.Div([
        html.H4("Explore categories", style={'textAlign': 'center', 'color': 'white'}),
        html.P("Detailed data is available for main and subcategories.", style={'textAlign': 'center', 'color': 'white'})
    ])




@app.callback(
    Output('subcategory-pie', 'figure'),
    Input('product-treemap', 'clickData'),
    prevent_initial_call=False  # Allow initial call to execute the callback with default values
)
def update_pie_chart(clickData):
    layout_options = {'title': 'Product Count by Category'}  # Default title

    if clickData and 'points' in clickData and len(clickData['points']) > 0 and 'id' in clickData['points'][0]:
        path = clickData['points'][0]['id'].split("/")
        category = path[0]

        if len(path) == 1:  # Main category clicked
            if globals().get('currentCategory') == category:
                # If clicking the same category again, reset to all categories
                fig = px.pie(df, values='product_count', names='main_business', title='Product Count by Category')
                globals()['currentCategory'] = None
                return apply_layout_options(fig, layout_options)
            else:
                # Show all subcategories for the clicked category
                filtered_df = df[df['main_business'] == category]
                # Filter out any subcategories with zero product count
                filtered_df = filtered_df[filtered_df['product_count'] > 0]
                layout_options['title'] = f'Total Product Count for {category}'
                fig = px.pie(filtered_df, values='product_count', names='category')
                globals()['currentCategory'] = category
                return apply_layout_options(fig, layout_options)
        else:
            # Subcategory or deeper level clicked
            if globals().get('currentCategory') != category:
                # New category clicked, show all its subcategories
                filtered_df = df[df['main_business'] == category]
                # Filter out any subcategories with zero product count
                filtered_df = filtered_df[filtered_df['product_count'] > 0]
                layout_options['title'] = f'Total Product Count for {category}'
                fig = px.pie(filtered_df, values='product_count', names='category')
                globals()['currentCategory'] = category
                return apply_layout_options(fig, layout_options)
            else:
                # Still in the same category, maintain subcategory view
                filtered_df = df[df['main_business'] == category]
                # Filter out any subcategories with zero product count
                filtered_df = filtered_df[filtered_df['product_count'] > 0]
                layout_options['title'] = f'Total Product Count for {category}'
                fig = px.pie(filtered_df, values='product_count', names='category')
                return apply_layout_options(fig, layout_options)
    else:
        # Reset to full category view if clickData is not usable
        fig = px.pie(df, values='product_count', names='main_business', title='Product Count by Category')
        globals()['currentCategory'] = None
        return apply_layout_options(fig, layout_options)



@app.callback(
    Output('price-range-bar', 'figure'),
    Input('product-treemap', 'clickData'),
    prevent_initial_call=False
)
def update_price_range_bar(clickData):
    layout_options = {'title': 'Price Range Distribution by Main Business'}

    if not clickData:
        agg_df = df.groupby(['price_range', 'main_business'], as_index=False)['product_count'].sum()
        fig = px.bar(agg_df, x='price_range', y='product_count', color='main_business',
                     category_orders={"price_range": ["Low", "Medium", "High"]})
        globals()['currentCategory'] = None
        return apply_layout_options(fig, layout_options)

    if 'points' in clickData and 'id' in clickData['points'][0]:
        path = clickData['points'][0]['id'].split("/")
        category = path[0]

        if len(path) == 1 and globals().get('currentCategory') == category:
            # Reset to full category view if the same category is clicked again
            globals()['currentCategory'] = None
            agg_df = df.groupby(['price_range', 'main_business'], as_index=False)['product_count'].sum()
            fig = px.bar(agg_df, x='price_range', y='product_count', color='main_business',
                         category_orders={"price_range": ["Low", "Medium", "High"]})
            return apply_layout_options(fig, layout_options)
        else:
            # Display data for all subcategories within the selected main category
            filtered_df = df[df['main_business'] == category]
            layout_options['title'] = f'Price Range Distribution for {category}'
            fig = px.bar(filtered_df, x='price_range', y='product_count', color='category',
                         category_orders={"price_range": ["Low", "Medium", "High"]})
            globals()['currentCategory'] = category
            return apply_layout_options(fig, layout_options)
    else:
        # Default to aggregated view if no specific interaction
        agg_df = df.groupby(['price_range', 'main_business'], as_index=False)['product_count'].sum()
        fig = px.bar(agg_df, x='price_range', y='product_count', color='main_business',
                     category_orders={"price_range": ["Low", "Medium", "High"]})
        globals()['currentCategory'] = None
        return apply_layout_options(fig, layout_options)


# Run the application
if __name__ == '__main__':
    app.run_server(port=8050, debug=True)
