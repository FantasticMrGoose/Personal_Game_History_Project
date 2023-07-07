import pandas as pd
import numpy as np
games_df = pd.read_csv('game_info_main.csv')

# Categorize unique values into a table
def categorize(item, col_name):
    unique_item = {
        col_name + " ID":[],
        col_name :[]                
    }

    i = 1
    for item in item:
        item = str(item)
        temp_item = item.split(",")
        for x in temp_item:
            x = x.strip()
            if x not in unique_item[col_name]:
                unique_item[col_name + " ID"].append(i)
                unique_item[col_name].append(x)
                i = i + 1

    #print(unique_item)

    #create junction table
    junction_table(col_name, unique_item)

    item_list = pd.DataFrame(unique_item)
    item_list.to_csv(f'{col_name.lower()}.csv', index=False)

#creates a junction table to bridge many-many relation
def junction_table (table_name, table):

    junction_table = {
        "Steam ID" : [],
        table_name + " ID" : []
    }

    for game, row in games_df.iterrows():
        temp_category = str(row[table_name])
        category = temp_category.split(",")
        
        for item in category:
            item = item.strip()

            #finds corrosponding unique ID from value
            for i in range(len(table[table_name])):
                if table[table_name][i] == item:
                    junction_table[table_name + " ID"]\
                        .append(table[table_name + " ID"][i])
                    junction_table["Steam ID"].append(row["Steam ID"])
                    i = i+1
                    
    
    junction_table = pd.DataFrame(junction_table)
    junction_table.to_csv(f'game{table_name}_JT.csv', index=False)

def main():

    #extract values from df
    dev = games_df["Developer"].values
    pub = games_df["Publisher"].values
    genre = games_df["Genre"].values
    cat = games_df["Categories"].values

    categorize(genre, "Genre"),
    categorize(dev, "Developer"),
    categorize(pub, "Publisher"),
    categorize(cat, "Categories"),

main()