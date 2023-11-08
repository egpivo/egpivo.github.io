---
title: "Note: Spark + R with `sparklyr`"
date: "2017-07-17"
layout: post
output:
  html_document
tags: [R]
---



[Apache Spark](https://spark.apache.org) is designed to process large-scale datasets efficently. Thanks to the authors of `sparklyr` package for using R code on a Spark cluster, e.g.,
easily manipulating datasets, and performing machine learning algorithms. 


## Installation
- Java: 
    1. Mac: 
        ```brew cask install java ```
    2. CentOS:
        ```sudo yum install java-1.7.0-openjdk-devel ```
    3. Other operating systems: https://www.java.com/en/download/help/download_options.xml
- Rsutdio + 'sparklyr': 
    - ``` install.packages("sparklyr")```
    - Set an environment variable Spark if needed: ```Sys.setenv(SPARK_HOME = "where_you_install_spark")```
    - More details: http://spark.rstudio.com
   
## Process:
  - Connection: ```spark_connect()```
  - I/O:
      - list the data frames available in Spark: ```src_tbls(spark_conn)```
      - write the data into Spark:
          - ```spark_write_csv(r_dataframe, filename)```
          - ```spark_write_parquet(r_dataframe, filename)```
          - ```spark_write_json(r_dataframe, filename)```
      - import the data into Spark:   
          - ```spark_read_csv(connection, "tbl_name", dir_path)```
          - ```spark_read_parquet(connection, "tbl_name", dir_path)```
          - ```spark_read_json(connection, "tbl_name", dir_path)```
  - Data wrangling: 
       -  link to data in Spark: ```tbl(connection,  dataname)```
          - see dimensionality of a dataframe from Spark:  ```dim(df_tbl)```
          - print 10 rows with all columns```print(df_tbl, n = 10, width = Inf)```
          - examine structure of a dataframe from Spark: ```glimpse(track_metadata_tbl)```
       - work with dplyr:
          1. select columns: ```select()```
              - select columns starting with a string: ```select(starts_with("some string"))```
              - select columns ending with a string: ```select(ends_with("some string"))```
              - select columns containing with a string: ```select(contains("some string"))```
              - select columns matching with a regex: ```select(matches("regex"))```
          2. select rows: ```distinct()```
              - count the unqiue values: ```count()```
              - show the top n rows: ```top_n()```
          2. filter rows: ```filter()```
          3. arrange rows: ```arrange()```
          4. change/add columns: ```mutate()```
          5. summarize statistics: ```summarize()```
          6. group by unquoted names of columns: ```group_by()```
          7. join tables:
              - left join by columns: ```left_join(, by = cols)```
              - anti join by columns: ```anti_join(, by = cols)```
              - semi join by columns: ```semi_join(, by = cols)```
       - copy an R dataframe to Spark: ```copy_to(connection, df)```
       - collect data back from Spark with a name: ```collect('name_in_spark')```
       - store the results of intermediate calculations: ```compute()``` 
       - covert R code into SQL and return the results to R immediately:```dbGetQuery(connection, query)```
  - Machine learning with MLlib:  
       - feature transformation functions named starting with "ft_" or "sdf_"
          - binarize continuous variables to logical with a threshold:  ```ft_binarizer("target_col", "new_col", threshold = a)```
          - bucketize continuous variables into categorical with a set of thresholds: ```ft_bucketizer("target_col", "new_col", splits = vec)```
          
          - quantilize continuous variables into categorical with a number of groups: ```ft_quantile_discretizer("target_col", "new_col", n.buckets = n)```     - tokenize simply```ft_tokenizer('target_col', 'new_col')```
          - tokenize with regex ```ft_regex_tokenizer('target_col', 'new_col', pattern)```
          - arrange rows using a Spark function: ```sdf_sort()```
          - exploring the columns of a tibble: ```sdf_schema(spark_tbl)```
          - sample the data without replacement, with a rate of fraction and a seed: ```sdf_sample(tbl, fraction = fraction, replacement = FALSE, seed = seed)```
          - split data into training and testing sets:
       ```sdf_partition(training = training_rate, testing = testing_rate)```
      - machine learning functions named starting with "ml_"
          - linear regression:```ml_linear_regression(response, feature)```
          - gradient boosted tree:
          ```ml_gradient_boosted_trees(response, feature)```             - random forest: ```ml_random_forest(response, feature)```
          - predict: ```sdf_predict(spark_model, testing_set)```
          - more models can be found on http://spark.rstudio.com/mllib.html
  - Disconnection: ```spark_connect()```
        

## References
* DataCamp: [Introduction to Spark in R using sparklyr](https://www.datacamp.com/courses/introduction-to-spark-in-r-using-sparklyr).
