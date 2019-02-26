from bokeh.plotting import figure, output_notebook, show,output_file
from bokeh.layouts import WidgetBox, row, column
from bokeh.models.widgets import Button, RadioButtonGroup, Select, Slider,PreText,CheckboxGroup
from bokeh.models import ColumnDataSource,Select,Panel,Legend
from bokeh.io import curdoc
from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.palettes import Spectral4
from bokeh.layouts import gridplot

def Fluctuation_Analysis_tab(monthly_data_deseasonalize):

    def create_figure():

        feature   = [feature_selection.labels[i] for i in feature_selection.active]
        commodity = commodity_selection.value
        apmc      = apmc_selection.value
        p_fluc    = [perc_fluc_selection.labels[i] for i in perc_fluc_selection.active]

        #subset to Commodity
        subset_1 = monthly_data_deseasonalize[monthly_data_deseasonalize['commodity']==commodity]

        #subset to APMC
        subset_2 = subset_1[subset_1['APMC']==apmc]

        # Subset to the feature
        subset_3 = subset_2[['date']+feature]

        #subset to perc_fluc feature
        subset_4 = subset_2[['date']+p_fluc]

        # Blank plot with correct labels
        p = figure(plot_width = 1000, plot_height = 400, x_axis_type='datetime',toolbar_location='below')
        legend_items = []
        for column,color in zip(subset_3.columns[1:],Spectral4):
            column_dict = {}
            column_dict['date']    = list(subset_3.date)
            column_dict['Feature'] = list(subset_3[column])
            # Line glyphs
            r = p.line(column_dict['date'],column_dict['Feature'],line_width=2,color=color, muted_color=color,muted_alpha=0.15)
            legend_items.append((column,[r]))

        q = figure(plot_width = 1000, plot_height = 400, x_axis_type='datetime',toolbar_location='below')
        legend_items_p_fluc = []
        for column,color in zip(subset_4.columns[1:],Spectral4):
            column_dict = {}
            column_dict['date']    = list(subset_4.date)
            column_dict['Feature'] = list(subset_4[column])
            # Line glyphs
            r2 = q.line(column_dict['date'],column_dict['Feature'],line_width=2,color=color, muted_color=color,muted_alpha=0.15)
            legend_items_p_fluc.append((column,[r2]))


        # Styling
        p = style(p)
        q = style(q)

        #Adding legend for p
        legend = Legend(items=legend_items)
        legend.click_policy="mute"
        p.add_layout(legend, 'right')
        p.title.text = "APMC: "+apmc_selection.value+" | Commodity: "+commodity_selection.value

        #Adding legend for q
        legend2 = Legend(items=legend_items_p_fluc)
        legend2.click_policy="mute"
        q.add_layout(legend2, 'right')
        q.title.text = "% fluctuation of de-seasonalized modal price with MSP"

        # put all the plots in an HBox
        pq = gridplot([[p, None], [q, None]])

        return pq


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

    col_list_monthly_data = list(monthly_data_deseasonalize.columns)
    col_list_perc_fluc    = list(monthly_data_deseasonalize.columns)

    col_list_monthly_data.remove('APMC')
    col_list_monthly_data.remove('commodity')
    col_list_monthly_data.remove('date')
    col_list_monthly_data.remove('APMC_Commodity')
    col_list_monthly_data.remove('Seasonality_type')
    col_list_monthly_data.remove('Seasonal_Component')
    col_list_monthly_data.remove('year')
    col_list_monthly_data.remove('Type')
    col_list_monthly_data.remove('msp_filter')
    col_list_monthly_data.remove('Percentage_fluc_des')
    col_list_monthly_data.remove('Percentage_fluc_raw')

    col_list_perc_fluc.remove('APMC')
    col_list_perc_fluc.remove('commodity')
    col_list_perc_fluc.remove('date')
    col_list_perc_fluc.remove('APMC_Commodity')
    col_list_perc_fluc.remove('Seasonality_type')
    col_list_perc_fluc.remove('Seasonal_Component')
    col_list_perc_fluc.remove('year')
    col_list_perc_fluc.remove('Type')
    col_list_perc_fluc.remove('msp_filter')
    col_list_perc_fluc.remove('modal_price')
    col_list_perc_fluc.remove('modal_price_deseasonalized')
    col_list_perc_fluc.remove('msprice')


    available_features = col_list_monthly_data
    #Feature Selection Widget
    feature_selection = CheckboxGroup(labels=sorted(available_features),active = [0, 1])
    feature_selection.on_change('active', update)

    perc_fluc = col_list_perc_fluc
    #Feature Selection Widget
    perc_fluc_selection = CheckboxGroup(labels=sorted(perc_fluc),active = [0, 1])
    perc_fluc_selection.on_change('active', update)

    available_commodities = list(monthly_data_deseasonalize.commodity.unique())
    #Commodity Selection Widget
    commodity_selection = Select(title='Commodity',value=available_commodities[0],options=sorted(available_commodities))
    commodity_selection.on_change('value',update)

    available_apmcs = list(monthly_data_deseasonalize.APMC.unique())
    #APMC selection widget
    apmc_selection = Select(title='APMC',value=available_apmcs[0],options=sorted(available_apmcs))
    apmc_selection.on_change('value',update)


    # Put controls in a single element
    controls = WidgetBox(commodity_selection,apmc_selection,feature_selection,perc_fluc_selection)

    # Create a row layout
    layout = row(controls, create_figure())

    # Make a tab with the layout
    tab = Panel(child=layout, title = 'Compare Features')

    return tab
