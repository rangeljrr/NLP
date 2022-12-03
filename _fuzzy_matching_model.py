# Import dependencies
from fuzzywuzzy import fuzz

def score_strings(string1, string2):
    """About:
          This function will take two strings as inputs and find the 
          ratio, partial_ratio, and token_sort_ratio scores. The scores will
          then be ensembled to create 1 final score
       
       Arguments:
           string1 (str): This will be a string input used to score against string2
           string2 (str): This will be a string input used to score against string1
           
       Returns:
           score (int): The function will return a score between 0 and 100
                        Higher scores indicate high probability of match and a low score
                        indicates a low probability of match between string1 and string2"""
    
    # Computing the ratio, partial ratio, and token sort ratio scores
    ratio_score = fuzz.ratio(string1, string2)
    partial_ratio_score = fuzz.partial_ratio(string1, string2)
    token_sort_ratio_score = fuzz.token_sort_ratio(string1, string2)
    
    # Ensembling the scores to create 1 single output
    ensembled_score = int((ratio_score + partial_ratio_score + token_sort_ratio_score) / 3)
    
    return ensembled_score

def token_intersection(str1, str2):
    """About:
          This funciton will take two strings, split the strings into tokens, 
          and find the lenth of common tokens
    
       Arguments:
          str1 (str): First String
          str2 (str): Second String
          
       Returns:
          Number of intersection tokens between str1 and str2
          """
    
    str1 = set(str1.split())
    str2 = set(str2.split())
    
    
    return len(str1.intersection(str2))

def roddys_name_address_fuzzy_matching(customer_database, incoming_data, use_token_reduction=True):
    """This function will take a customer database and match any incoming data to the database,
       using fuzzy logic matching. It will then use token_intersection() to tokenize the data and 
       reduce the dimensionality (optional) and then apply the fuzzy logic ensebling to find the best 
       possible matches. Note that this funciton will only return the single best match.
       
       Arguments:
          customer_database (pd.DataFrame): This is the internal customer database
          incoming_data (pd.DataFrame: This is the data we are checking against the customer
                                       database
       Returns:
          match_results (pd.DataFrame): A dataframe that matches the incoming dataframe """
    
    match_results = []
    # For each value in March, we want to find any matches that have a score above 90
    for i in range(incoming_data.shape[0]):

        # Bill Information
        name = incoming_data.iloc[i]['Name']
        address = incoming_data.iloc[i]['Address']
        city = incoming_data.iloc[i]['City']
        zip_code = incoming_data.iloc[i]['Zip']
        state = incoming_data.iloc[i]['State']
        name_address = incoming_data.iloc[i]['Name_Address']

        # First Narrow down the fields using a common score (intersection)
        if use_token_reduction == True:
            fuzzy_dataframe = customer_database.copy()
            fuzzy_dataframe['scores'] = fuzzy_dataframe['Name_Address'].apply(lambda x: token_intersection(x,name_address))# <-- Will need to rename and redo this algorithm
            most_common = max(fuzzy_dataframe['scores'])
            fuzzy_dataframe = fuzzy_dataframe[fuzzy_dataframe['scores'] == most_common]

        # Do not use token reduction
        else:
            fuzzy_dataframe = customer_database.copy()

        # Need to create the distance array from the dictionary
        fuzzy_dataframe['scores'] = fuzzy_dataframe['Name_Address'].apply(lambda x: score_strings(x,name_address))
        max_score = max(fuzzy_dataframe['scores'])
        best_match = fuzzy_dataframe[fuzzy_dataframe['scores'] == max_score].iloc[0]
        
        # Next we need to store values (Match Information)
        match_name = fuzzy_dataframe.iloc[0]['Name']
        match_address = fuzzy_dataframe.iloc[0]['Address']
        match_city = fuzzy_dataframe.iloc[0]['City']
        match_zip_code = fuzzy_dataframe.iloc[0]['Zip']
        match_state = fuzzy_dataframe.iloc[0]['State']

        # Finally, we want to match the address and name to out over best match
        address_score = score_strings(address,match_address)
        name_score = score_strings(name,match_name)
        
        match_results.append([name,address,city,zip_code,state,
                              match_name,match_address,match_city,match_zip_code,match_state,
                              max_score, address_score,name_score])

    match_results = pd.DataFrame(match_results, columns=['Bill Name','Bill Address','Bill City','Bill Zip','Bill State',
                                                         'Match Name','Match Address','Match City','Match Zip','Match State',
                                                         'Overall Match Score', 'Address Score','Name Score'])
    return match_results


####################################################################################################
#                                    How to use the model in a loop                                #
####################################################################################################
"""
match_results = pd.DataFrame()
total = 0

# We will iterate through 3 digit zips (Can be state, last name, etc.)
for z in zips3[0:2]:

    # Subsetting data by 3Zip
    iter_dict = customer_root_dictionary[customer_root_dictionary['Zip3'] == z]
    iter_march = march_example[march_example['Zip3'] == z]
    total += iter_march.shape[0]
    
    # Need to append results to master dataframe (match_results)
    iter_match_results = roddys_name_address_fuzzy_matching(iter_dict, iter_march, use_token_reduction=True)
    match_results = pd.concat([match_results, iter_match_results], axis=0)
    
match_results.reset_index(inplace=True, drop=True)
"""