from openbb import obb as openbb


class Indices:

    def __init__(self):
        
        self.indices_folder = "data/indices"
        self.index_list = ['VIX', 'MOVE','SKEW','SPX']


    def get_index(self, symbol):
      
        return openbb.index.price.historical(symbol=symbol, provider='yfinance').to_df()
       

    def get_indices(self):
    
        for index in self.index_list:
            index= '^'+index
            df = self.get_index(index)
            df.to_csv(self.indices_folder + '/' + index +'csv', index=True)
            #print (df.tail(2))