
  1.bokeh 0.12.16

The main application is located in the `EDA_Bokeh` folder. To run the application, open a command prompt, change to the directory containing `EDA_Bokeh` and run `bokeh serve --show EDA_Bokeh/`. This runs a bokeh server locally and will automatically open the interactive dashboard in your browser at `localhost:5006`.

Copy this config and use it this as a template.
### Config File Description
`INPUT` Section consist for Reading and Filtering Data.
1. input_location        - location of folder where datframe is located
2. file_name_cmo_monthly - name of monthly data frame of cmo in the input_location
3. file_name_mandi       - name of CMO_MSP_Mandi dataframe saved in the input lcoation
4. nthreads              - number of threads in the system used to read the dataframe
5. apmc                  - provide names of APMC,if any, for which dataframe is to be subsetted. If left blank then it will                              read all apmcs
6. commodity             - provide names of commodities, if any, for which dataframe is to be subsetted. If left blank then it                            will read all commodities
7. save_filtered_df      - Whether to save or not save the filtered and subsetted dataframe in the input location. Takes the                              value TRUE or FALSE
8. correct_spelling      - TRUE or FALSE. If TRUE it will correct spellings of commodities specified in the spelling_dict
9. spelling_dict         - a dictionary of incorrect:correct spelling as key:value of commodities. Ignored if                                            correct_spelling=FALSE

`OUTLIER` section is for filtering the data for outliers
1. remove_outliers = TRUE or FALSE. If TRUE removes outliers using IQR score.
