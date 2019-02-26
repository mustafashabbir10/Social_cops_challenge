from bokeh.plotting import figure, output_notebook, show,output_file
from bokeh.layouts import WidgetBox, row, column
from bokeh.models.widgets import Button, RadioButtonGroup, Select, Slider,PreText,CheckboxGroup
from bokeh.models import ColumnDataSource,Select,Panel,Legend
from bokeh.io import curdoc
from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.palettes import Spectral4

def Compare_Features_tab(monthly_data,cmo_mandi):

    def create_figure():

        feature   = [feature_selection.labels[i] for i in feature_selection.active]
        commodity = commodity_selection.value
        apmc      = apmc_selection.value

        #subset to Commodity
        subset_1 = monthly_data[monthly_data['Commodity']==commodity]

        #subset to APMC
        subset_2 = subset_1[subset_1['APMC']==apmc]

        # Subset to the feature
        subset_2 = subset_2[['date']+feature]

        # Blank plot with correct labels
        p = figure(plot_width = 1000, plot_height = 400, x_axis_type='datetime',toolbar_location='below')
        legend_items = []
        for column,color in zip(subset_2.columns[1:],Spectral4):
            column_dict = {}
            column_dict['date']    = list(subset_2.date)
            column_dict['Feature'] = list(subset_2[column])
            # Line glyphs
            r = p.line(column_dict['date'],column_dict['Feature'],line_width=2,color=color, muted_color=color,muted_alpha=0.15)
            legend_items.append((column,[r]))

        # Styling
        p = style(p)

        #Adding legend
        legend = Legend(items=legend_items)
        legend.click_policy="mute"
        p.add_layout(legend, 'right')
        p.title.text = "APMC: "+apmc_selection.value+" | Commodity: "+commodity_selection.value

        return p


    def style(p):
        # Title
        p.title.align          = 'center'
        p.title.text_font_size = '16pt'
        p.title.text_font      = 'serif'

        # Axis titles
        p.xaxis.axis_label = 'Date'
        p.xaxis.axis_label_text_font_size  = '14pt'
        p.xaxis.axis_label_text_font_style = 'bold'
        p.yaxis.axis_label_text_font_size  = '14pt'
        p.yaxis.axis_label_text_font_style = 'bold'

        # Tick labels
        p.xaxis.major_label_text_font_size = '12pt'
        p.yaxis.major_label_text_font_size = '12pt'

        return p

    def update(attr, old, new):
        layout.children[1] = create_figure()

    col_list_monthly_data = list(monthly_data.columns)
    col_list_cmo_mandi    = list(cmo_mandi.columns)

    col_list_monthly_data.remove('APMC')
    col_list_monthly_data.remove('APMC-Commodity')
    col_list_monthly_data.remove('Commodity')
    col_list_monthly_data.remove('Year')
    col_list_monthly_data.remove('Month')
    col_list_monthly_data.remove('date')
    col_list_monthly_data.remove('district_name')
    col_list_monthly_data.remove('state_name')

    available_features = col_list_monthly_data
    #Feature Selection Widget
    feature_selection = CheckboxGroup(labels=sorted(available_features),active = [0, 1])
    feature_selection.on_change('active', update)

    available_commodities = list(monthly_data.Commodity.unique())
    #Commodity Selection Widget
    commodity_selection = Select(title='Commodity',value=available_commodities[0],options=sorted(available_commodities))
    commodity_selection.on_change('value',update)

    available_apmcs = list(monthly_data.APMC.unique())
    #APMC selection widget
    apmc_selection = Select(title='APMC',value=available_apmcs[0],options=sorted(available_apmcs))
    apmc_selection.on_change('value',update)


    # Put controls in a single element
    controls = WidgetBox(commodity_selection,apmc_selection,feature_selection)

    # Create a row layout
    layout = row(controls, create_figure())

    # Make a tab with the layout
    tab = Panel(child=layout, title = 'Compare Features')

    return tab
