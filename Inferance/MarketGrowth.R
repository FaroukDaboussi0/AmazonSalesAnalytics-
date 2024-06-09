library(forecast)
library(dplyr)
library(ggplot2)
library(zoo)
library(lubridate)
library(readxl)

sales_forecast_function <- function(country, product) {
  # Load the dataset (assuming an Excel file)
  sales_data <- read_excel("C:/ProjetBI/global_superstore_2016.xlsx") # Use forward slashes for portability
  
  # Ensure correct column name for the date
  date_column_name <- "Order Date"
  
  # Convert the date column to Date type
  sales_data[[date_column_name]] <- as.Date(sales_data[[date_column_name]], format = "%Y-%m-%d")
  
  # Filter data for the specified country and product
  filtered_data <- sales_data %>%
    filter(Region == country & `Sub-Category` == product)
  
  # Create a month column from the filtered data
  filtered_data$Month <- as.yearmon(filtered_data[[date_column_name]])
  
  # Aggregate sales by month
  monthly_sales <- filtered_data %>%
    group_by(Month) %>%
    summarise(Sales = sum(Sales))
  
  # Convert to time series object
  start_year <- as.integer(format(min(monthly_sales$Month), "%Y"))
  start_month <- as.integer(format(min(monthly_sales$Month), "%m"))
  
  sales_ts <- ts(monthly_sales$Sales, start = c(start_year, start_month), frequency = 12)
  
  # Split data into training and testing sets
  train_end <- length(sales_ts) - 12 # Use the last 12 months as test set
  train_ts <- window(sales_ts, end = c(start_year + (train_end %/% 12), train_end %% 12 + 1))
  test_ts <- window(sales_ts, start = c(start_year + (train_end %/% 12), train_end %% 12 + 2))
  
  # Perform grid search for best ARIMA parameters
  best_aic <- Inf
  best_order <- c(0, 0, 0)
  best_seasonal <- c(0, 0, 0, 0)
  
  for (p in 0:2) {
    for (d in 0:1) {
      for (q in 0:2) {
        for (P in 0:1) {
          for (D in 0:1) {
            for (Q in 0:1) {
              fit <- try(arima(train_ts, order = c(p, d, q), 
                               seasonal = list(order = c(P, D, Q), period = 12)), silent = TRUE)
              if (!is.element("try-error", class(fit))) {
                aic <- AIC(fit)
                if (aic < best_aic) {
                  best_aic <- aic
                  best_order <- c(p, d, q)
                  best_seasonal <- c(P, D, Q, 12)
                }
              }
            }
          }
        }
      }
    }
  }
  
  # Fit the best SARIMA model
  fit <- arima(train_ts, order = best_order, seasonal = list(order = best_seasonal[1:3], period = best_seasonal[4]))
  
  # Forecast for the test period
  forecast_period <- 12
  sales_forecast <- forecast(fit, h = forecast_period)
  # Evaluate the forecast
  forecast_values <- as.numeric(sales_forecast$mean)
  actual_values <- as.numeric(test_ts)
  mae <- mean(abs(forecast_values - actual_values))
  rmse <- sqrt(mean((forecast_values - actual_values)^2))
  
  print(paste("Best ARIMA Order:", paste(best_order, collapse = ",")))
  print(paste("Best Seasonal Order:", paste(best_seasonal[1:3], collapse = ","), "with period", best_seasonal[4]))
  print(paste("Mean Absolute Error (MAE):", mae))
  print(paste("Root Mean Squared Error (RMSE):", rmse))
  str(test_ts)
  
  # Plot using ggplot2
  ggplot(plot_data, aes(x = Date, y = Sales, color = Type)) +
    geom_line() +
    geom_point() +
    ggtitle(paste("Sales farouk Forecast vs Actual for", product, "in", country)) +
    xlab("Year") +
    ylab("Sales") +
    theme_minimal() +
    annotate("text", x = as.Date(paste0(start_year + (train_end %/% 12), "-01-01")), 
             y = max(test_ts, na.rm = TRUE), label = paste("MAE:", round(mae, 2), ", RMSE:", round(rmse, 2)), 
             color = "blue", hjust = 0)
}

# Example usage:
sales_forecast_function("Western Europe", "Binders")
print("salem")