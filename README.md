# Kalshi stuff
Having some fun with the kalshi api...

## data-pull: programs for pulling data from Kalshi's servers
 - get_historical_data.py (No API key Required)
   + Creates an organized directory of raw files downloaded from kashi.com/market-data
   + Takes the directory where you want to store the dataset as a command-line argument
   + Sets up a directory for you (cli-argument-path/kalshi-historical) on its first run and can be ran afterwards to update the dataset without redownloading old files.
   + Current size of dataset is around half a gigabyte as of 2025-05-30
   + I've considered compressing the files as I store them, but it's not an issue as of now
