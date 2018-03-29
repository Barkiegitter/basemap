import pandas as pd
import numpy as np

import yahoo_reader
import preprocessing as pp
import lstm_utils as utils
import lstm_model
import plotting
import pygmail
#%%
yr = yahoo_reader.finance_data(tickers=['OMEX','IFON', 'AMAG', 'BA'])
df_main = yr.get_data()

ticker_dict = {}
# Prep data for LSTM model
for ticker in yr.tickers:
    df = df_main[df_main.ticker == ticker].reset_index(drop=True)
    df_p = pp.pre_process_data(df, window_length=6)
#    df_t = pp.pre_process_data(df,window_length=5)
    # Split closing price into test and train
    close_nmd_array = utils.series_to_ndarray(df_p, column='close_nmd')
    x_train, y_train, x_test, y_test = utils.train_test_split(close_nmd_array)
    days_ahead=1
    # Build model
    model, mse = lstm_model.randomised_model_config(ticker,
                                                    df,
                                                    days_ahead,
                                                    x_train,
                                                    y_train, 
                                                    x_test,
                                                    y_test,
                                                    iterations=5,
                                                    epochs=8)

    # Create X based on last window in data (last window is 0)
    
    X, X_nmd = utils.gen_X(df_p, window=0)

    predictions_nmd = lstm_model.predict(model, X_nmd, days_ahead)
    predictions = (predictions_nmd + 1) * X[0][0]
    
    # Calculate predicted growth over 5 days
    growth = np.round(((predictions[0][4] / X[0][4]) -1) * 100, 2)[0]
    
    # Plot predictions
    plt = plotting.plot_latest_prediction(days_ahead,df, predictions, ticker, growth, mse,
                                          model, df_p,days_ahead)
    
    # Add predicted growth to ticker_dict
    ticker_dict[ticker] = growth

# Compose and send email
#subject, body, attachments = pygmail.compose_email(expected_deltas=ticker_dict)
#pygmail.send_mail(subject=subject,
#                  attachments=attachments, 
#                  body=body)