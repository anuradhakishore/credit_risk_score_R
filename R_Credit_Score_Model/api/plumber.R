library(plumber)
library(tidymodels)
library(tibble)
library(jsonlite)
library(dplyr)

model <- readRDS("api/final_xgb_model.rds")
cutoff <- readRDS("api/final_cutoff.rds")

api <- pr()

api <- pr_get(api, "/health", function() {
  list(status = "API is running")
})

api <- pr_post(api, "/predict", function(req) {
  
  tryCatch({
    
    body <- jsonlite::fromJSON(req$postBody)
    
    new_data <- tibble(
      RevolvingUtilizationOfUnsecuredLines = body$RevolvingUtilizationOfUnsecuredLines,
      age = body$age,
      `NumberOfTime30-59DaysPastDueNotWorse` = body$NumberOfTime30_59DaysPastDueNotWorse,
      DebtRatio = body$DebtRatio,
      MonthlyIncome = body$MonthlyIncome,
      NumberOfOpenCreditLinesAndLoans = body$NumberOfOpenCreditLinesAndLoans,
      NumberOfTimes90DaysLate = body$NumberOfTimes90DaysLate,
      NumberRealEstateLoansOrLines = body$NumberRealEstateLoansOrLines,
      `NumberOfTime60-89DaysPastDueNotWorse` = body$NumberOfTime60_89DaysPastDueNotWorse,
      NumberOfDependents = body$NumberOfDependents
    )
    
    prob <- predict(model, new_data, type = "prob")
    
    default_prob <- as.numeric(prob$.pred_1)
    
    pred <- ifelse(default_prob >= cutoff, "1", "0")
    
    risk_band <- case_when(
      default_prob < 0.10 ~ "Low Risk",
      default_prob < 0.25 ~ "Medium Risk",
      default_prob < 0.50 ~ "High Risk",
      TRUE ~ "Very High Risk"
    )
    
    list(
      default_probability = round(default_prob, 4),
      predicted_class = as.character(pred),
      cutoff_used = as.numeric(cutoff),
      risk_band = as.character(risk_band)
    )
    
  }, error = function(e) {
    list(
      error = e$message
    )
  })
})

api$run(host = "127.0.0.1", port = 8000)