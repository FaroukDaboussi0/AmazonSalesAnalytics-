# Installer et charger les packages nécessaires
install.packages("dplyr")
install.packages("lubridate")
install.packages("ggplot2")
install.packages("forecast")
install.packages("readxl")

library(dplyr)
library(lubridate)
library(ggplot2)
library(forecast)
library(readxl)
# Charger les données (remplacez 'your_data.csv' par le chemin de votre fichier de données)
data <- read_excel("C:/ProjetBI/global_superstore_2016.xlsx")  # Use forward slashes for portability



# Afficher les premières lignes du jeu de données
head(data)

# Afficher la structure du jeu de données
str(data)

#selectionner les columns a utiliser
columns_to_etude <- c("Order ID","Order Date","Region","Category","Sales")
data_needed <- data[,names(data) %in% columns_to_etude]
str(data_needed)
summary(data_needed)


# Example: Check for outliers in the 'Sales' column
ggplot(data, aes(x = Sales)) +
  geom_boxplot() +
  labs(title = "Sales Distribution", x = "Sales", y = "")



# Agréger les ventes par date
daily_sales <- data_needed %>%
  group_by(data_needed["Order Date"]) %>%
  summarise(Total_Sales = sum(Sales))

# Afficher les premières lignes des ventes agrégées
head(daily_sales)
summary(daily_sales)
View(daily_sales)

complete_dates <- seq.Date(from = as.Date("2012-01-01"), to = as.Date("2015-12-31"), by = "day")



length(complete_dates)
str(complete_dates)
str(daily_sales)
nrow(daily_sales)

#conclution is there is missing values in days sequance 



# Convert Order Date to Date type if it's not already
daily_sales$`Order Date` <- as.Date(daily_sales$`Order Date`)

# Create a complete data frame with Total_Sales set to NA initially
complete_data <- data.frame(`Order Date` = complete_dates)

names(daily_sales)
names(complete_data)


# Left join to keep all dates and fill in existing sales data
merged_data <- complete_data %>%
  left_join(daily_sales, by = c("Order.Date" = "Order Date"))

# Arrange the data by Order Date
merged_data <- merged_data %>%
  arrange(`Order.Date`)
nrow(merged_data)
View(merged_data)

# Function to calculate moving average for NA values
fill_na_with_moving_average <- function(data) {
  for (i in 1:nrow(data)) {
    if (is.na(data$Total_Sales[i])) {
      # Get indices for the window
      window_indices <- (i-2):(i+2)
      window_indices <- window_indices[window_indices > 0 & window_indices <= nrow(data)]
      
      # Calculate moving average excluding NA values
      data$Total_Sales[i] <- mean(data$Total_Sales[window_indices], na.rm = TRUE)
    }
  }
  return(data)
}

# Apply the function to fill missing values
filled_data <- fill_na_with_moving_average(merged_data)
summary(filled_data)

num_na <- sum(is.na(filled_data$Total_Sales))
num_na

# Convert filled_data to a time series object
sales_ts <- ts(filled_data$Total_Sales, start = c(2012, 1), frequency = 365)

# Check the structure of the time series object
str(sales_ts)


plot(sales_ts, main = "Daily Sales Time Series", ylab = "Total Sales", xlab = "Time")

#------------------
#----------------------*
#------------------------
# Identify outliers using the forecast package
# Function to detect outliers using Z-score
detect_outliers_zscore <- function(ts, threshold = 3) {
  mean_ts <- mean(ts)
  sd_ts <- sd(ts)
  z_scores <- (ts - mean_ts) / sd_ts
  return(which(abs(z_scores) > threshold))
}

# Identify outliers
outliers_zscore <- detect_outliers_zscore(sales_ts)

# Convert the time series to a data frame for ggplot2
ts_df <- data.frame(
  time = as.numeric(time(sales_ts)),
  value = as.numeric(sales_ts)
)

# Add a column to indicate outliers
ts_df$outlier <- ifelse(seq_along(sales_ts) %in% outliers_zscore, "Outlier", "Normal")

# Plot the time series with outliers highlighted
ggplot(ts_df, aes(x = time, y = value)) +
  geom_line() +
  geom_point(data = subset(ts_df, outlier == "Outlier"), color = "red", size = 2) +
  labs(title = "Time Series with Outliers", x = "Time", y = "Total Sales") +
  theme_minimal()

#-------------------
#-------------------
# Function to calculate moving average
calculate_moving_average <- function(ts, window_size = 7) {
  return(stats::filter(ts, rep(1/window_size, window_size), sides = 2))
}

# Calculate the moving average of the time series
moving_avg <- calculate_moving_average(sales_ts)

if (!require(lubridate)) install.packages("lubridate")
library(lubridate)
# Extract dates of outliers
outlier_dates <- time(sales_ts)[outliers_zscore]

# Convert fractional years to Date objects

convert_fractional_year_to_date <- function(fractional_year) {
  year <- floor(fractional_year)
  fractional_part <- fractional_year - year
  days_in_year <- ifelse(leap_year(year), 366, 365)
  day_of_year <- round(fractional_part * days_in_year)
  as.Date(paste0(year, "-01-01")) + days(day_of_year - 1)
}

# Convert outlier dates from fractional years to Date objects
outlier_dates_as_dates <- as.Date(sapply(outlier_dates, convert_fractional_year_to_date))

# Print outlier dates in a more readable format
print(outlier_dates_as_dates)
# Replace outliers with moving average values
sales_ts_no_outliers <- sales_ts
sales_ts_no_outliers[outliers_zscore] <- moving_avg[outliers_zscore]

# Plot original time series with outliers
autoplot(sales_ts, main = "Original Time Series with Outliers")

# Plot modified time series without outliers
autoplot(sales_ts_no_outliers, main = "Time Series with Outliers Replaced by Moving Average")
#------------------

# Apply seasonal decomposition
decomposed_data <- decompose(sales_ts)

# Plot the decomposed data
plot(decomposed_data)
sales_ts_withoutsai <- sales_ts - decomposed_data$seasonal
plot(sales_ts_withoutsai)
# Load necessary library
library(tseries)
#test of stationarity
# Perform the ADF test
adf_test <- adf.test(sales_ts_no_outliers)

# Print the test result
adf_test
acf(sales_ts_no_outliers)
pacf(sales_ts)
num_nn = sum(is.na(sales_ts_withoutsai))
num_nn
#sales_ts_withoutsai <- log1p(sales_ts_withoutsai)
plot(sales_ts)
sales_ts_lag <- diff(sales_ts_no_outliers ,lag = 7)
#test of stationarity
adf_test <- adf.test(sales_ts)
adf_test
acf(sales_ts_lag) #the acf change diviation after LAG 1
pacf(sales_ts ) # the pacf begin to get lower slowly after lag 1
#ts now is stationnair
# conclution arema orders are c(1,0,1)
arima_order <- c(7, 0, 2)
arima_model <- Arima(sales_ts_lag, order = arima_order)
checkresiduals(arima_model)

#------------------------------
#------------------------------
#------------------------------

# Rename specific columns of filled_data
colnames(filled_data) <- c("ds", "y")

# Verify the changes
print(colnames(filled_data))

#-----------------------------

library(MASS)

# Estimate lambda using boxcox
lambda <- boxcox(y ~ 1, data = filled_data)$x[which.max(boxcox(y ~ 1, data = filled_data)$y)]

# Apply Box-Cox transformation
if (lambda == 0) {
  filled_data$y_transformed <- log(filled_data$y + 1)
} else {
  filled_data$y_transformed <- (filled_data$y^lambda - 1) / lambda
}

# Check the stability of the transformed values
stability <- sd(filled_data$y_transformed)
cat("Stability of transformed values:", stability, "\n")

#----------------------------

library(prophet)
# Fit the Prophet model

#lambda <- BoxCox.lambda(filled_data$y, method="loglik")
#filled_data$y <- BoxCox(filled_data$y, lambda)
#filled_data$y <- diff(filled_data$y)
filled_data$y <- log(filled_data$y)
z_score_normalized <- scale(filled_data$y)
z_score_normalized
filled_data$y <- z_score_normalized
model <- prophet(filled_data)

# Create a dataframe for future dates (e.g., next 30 days)
future <- make_future_dataframe(model, periods = 30)

# Generate the forecast
forecast <- predict(model, future)

# Plot the forecast
plot(model, forecast)

# Plot the forecast components (trend, weekly seasonality, yearly seasonality)
prophet_plot_components(model, forecast)

# Optional: Evaluate the model if you have a test set
# Split the data into training and test sets
train_size <- floor(0.8 * nrow(filled_data))
train_data <- filled_data[1:train_size, ]
test_data <- filled_data[(train_size + 1):nrow(filled_data), ]

# Fit the Prophet model to the training set
model_train <- prophet(train_data)

# Create a dataframe for future dates based on the length of the test set
future_test <- make_future_dataframe(model_train, periods = nrow(test_data))

# Generate the forecast
forecast_test <- predict(model_train, future_test)

# Extract the forecasted values for the test period
forecasted_values <- forecast_test$yhat[(nrow(future_test) - nrow(test_data) + 1):nrow(future_test)]

# Calculate accuracy metrics
library(Metrics)
rmse_test <- rmse(test_data$y, forecasted_values)
mae_test <- mae(test_data$y, forecasted_values)
mape_test <- mape(test_data$y, forecasted_values)

# Print the accuracy metrics
cat("RMSE:", rmse_test, "\n")
cat("MAE:", mae_test, "\n")
cat("MAPE:", mape_test, "\n")

# Plot actual vs forecasted values
plot(test_data$ds, test_data$y, type = "l", col = "red", xlab = "Date", ylab = "Sales", main = "Actual vs Forecasted Sales")
lines(test_data$ds, forecasted_values, col = "blue")
legend("topleft", legend = c("Actual", "Forecasted"), col = c("red", "blue"), lty = 1)

#--------------
#----------------
#----------------

str(filled_data)
head(filled_data)
# Install required packages (if not already installed)
if (!require(keras)) install.packages("keras")
if (!require(dplyr)) install.packages("dplyr")
if (!require(tidyr)) install.packages("tidyr")
library(keras)
library(dplyr)
library(tidyr)
# Normalize the differenced data

filled_data$Total_Sales <- log(filled_data$Total_Sales)




# Create sequences
create_sequences <- function(data, n) {
  x <- NULL
  y <- NULL
  for (i in 1:(nrow(data) - n)) {
    x <- rbind(x, data[i:(i + n - 1), 2])
    y <- c(y, data[i + n, 2])
  }
  return(list(x = array(x, dim = c(nrow(x), n, 1)), y = y))
}

# Parameters
n_timesteps <- 7
train_size <- floor(0.8 * nrow(filled_data))
train_data <- filled_data[1:train_size,]
test_data <- filled_data[(train_size + 1):nrow(filled_data),]

train_sequences <- create_sequences(train_data, n_timesteps)
test_sequences <- create_sequences(test_data, n_timesteps)

# Build the LSTM model
model <- keras_model_sequential() %>%
  layer_lstm(units = 32, return_sequences = TRUE, input_shape = c(n_timesteps, 1)) %>%
  layer_lstm(units = 64) %>%
  layer_dense(units = 1)

model %>% compile(
  loss = 'mean_squared_error',
  optimizer = 'adam'
)

# Train the model
history <- model %>% fit(
  train_sequences$x, train_sequences$y,
  epochs = 100,
  batch_size = 32,
  validation_split = 0.2,
  callbacks = list(callback_early_stopping(monitor = "val_loss", patience = 10))
)

# Evaluate the model
results <- model %>% evaluate(test_sequences$x, test_sequences$y)
print(results)

# Make predictions
predictions <- model %>% predict(test_sequences$x)

# Denormalize the predictions
predictions <- predictions * (max_value - min_value) + min_value

# Inverse differencing (add the last actual value to each predicted difference)
last_actual <- log(filled_data$Total_Sales[train_size]) # Last value before the test set
predictions <- exp(cumsum(c(last_actual, predictions)))[-1]

# Compare the predictions with actual values
actual_values <- exp(filled_data$Total_Sales[(train_size + n_timesteps + 1):nrow(filled_data)])

results <- data.frame(
  Date = filled_data$Order.Date[(train_size + n_timesteps + 1):nrow(filled_data)],
  Actual = actual_values,
  Predicted = predictions
)
print(results)

# Plot the results
library(ggplot2)

ggplot(results, aes(x = Date)) +
  geom_line(aes(y = Actual, color = "Actual")) +
  geom_line(aes(y = Predicted, color = "Predicted")) +
  labs(title = "Actual vs Predicted Sales", y = "Sales", x = "Date") +
  theme_minimal()




#-----------------------------------
# Log transform to stabilize variance
filled_data$Total_Sales <- log(filled_data$Total_Sales)

# Create a new column for differenced values
filled_data$Diff_Sales <- c(NA, diff(filled_data$Total_Sales))

# Remove the first row with NA value in the differenced column
filled_data <- filled_data[-1, ]

# Standardize the differenced data
mean_value <- mean(filled_data$Diff_Sales)
std_value <- sd(filled_data$Diff_Sales)
filled_data$Diff_Sales <- scale(filled_data$Diff_Sales, center = mean_value, scale = std_value)
head(filled_data)
filled_data <- filled_data[, !(names(filled_data) %in% c("Total_Sales"))]
plot(filled_data)
train_size <- floor(0.8 * nrow(filled_data))
train_data <- filled_data[1:train_size,]
test_data <- filled_data[(train_size + 1):nrow(filled_data),]
# Parameters
n_timesteps <- 7  # Adjust as needed

# Reshape input data to add timestep dimension
train_sequences$x <- array_reshape(train_sequences$x, c(dim(train_sequences$x), 1))
test_sequences$x <- array_reshape(test_sequences$x, c(dim(test_sequences$x), 1))

# Build the LSTM model
model <- keras_model_sequential() %>%
  layer_lstm(units = 16, return_sequences = TRUE, input_shape = c(n_timesteps, 1)) %>%
  layer_lstm(units = 64) %>%
  layer_dense(units = 1)

model %>% compile(
  loss = 'mean_squared_error',
  optimizer = 'adam'
)

# Train the model
history <- model %>% fit(
  train_sequences$x, train_sequences$y,
  epochs = 100,  # Adjust as needed
  batch_size = 32,  # Adjust as needed
  validation_split = 0.2,
  callbacks = list(callback_early_stopping(monitor = "val_loss", patience = 10))
)
cat("Shape of train_sequences$x:", dim(train_sequences$x), "\n")
cat("Shape of test_sequences$x:", dim(test_sequences$x), "\n")
