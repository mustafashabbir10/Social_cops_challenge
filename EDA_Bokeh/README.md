Requirements:

  1.bokeh 0.12.16

The main application is located in the `EDA_Bokeh` folder. To run the application, open a command prompt, change to the directory containing `EDA_Bokeh` and run `bokeh serve --show EDA_Bokeh/`. This runs a bokeh server locally and will automatically open the interactive dashboard in your browser at `localhost:5006`.

Copy this config and use it this as a template.
### Config File Description
`INPUT` Section consist for Reading and Filtering Data.
Currently it's capability is limited to read data only from local.

2 type of Data version(filetype) Site and year.

Filters
- cols_req - if plotting interactive screen need only few features.(Device and TimeStamp must be included)
ex. Device,TimeStamp,feature_1,feature_2
- machines - Subset of machines needed for particular interactive plot
ex. T01,T02,T03
- years - filter only for one or multiple years
ex. 2017,2018
