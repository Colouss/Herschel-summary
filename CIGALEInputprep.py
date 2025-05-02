import pandas as pd
import numpy as np  # Also needed for np.sqrt()

#turning inverse variance into uncertainty
def inverse_variance_into_uncertainty(input_file, output_file):
    # Load the CSV file
    df = pd.read_csv(input_file)
    
    # Loop through the columns
    for col in df.columns:
        if col.startswith('FLUX_IVAR_AP06'):
            # Calculate the uncertainty from the inverse variance
            new_col_name = col.replace('FLUX_IVAR_AP06', 'FLUX_UNCERT_AP06')
            df[new_col_name] = 1 / np.sqrt(df[col])
    
    # Drop the original FLUX_IVAR_AP06 columns if needed
    df.drop(columns=[col for col in df.columns if col.startswith('FLUX_IVAR_AP06')], inplace=True)

    # Save the modified DataFrame to a new CSV file
    df.to_csv(output_file, index=False)

    print(f"File successfully written to {output_file}")
#adding extinction into the template table
def multiply_columns_and_save(file1, file2, column_pairs, output_file):
    # Load the CSV files
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    
    # Initialize a DataFrame to store the results
    result_df = df1.copy()

    # Multiply each pair of columns and store the result in the result_df
    for col1, col2 in column_pairs:
        if col1 not in df1.columns:
            raise ValueError(f"Column '{col1}' not found in {file1}")
        if col2 not in df2.columns:
            raise ValueError(f"Column '{col2}' not found in {file2}")
        
        # Perform the multiplication with extinction correction
        result_df[col1] = df1[col1] * (10 ** (df2[col2] / 2.5))
        
        # Replace 0, infinity, or very large/small values with NaN
        result_df[col1] = result_df[col1].replace([0, np.inf, -np.inf], 'nan')
    
    # Save the resulting DataFrame to a new CSV file
    result_df.to_csv(output_file, index=False)

    print(f"Result successfully written to {output_file}")
# Function to convert a .fits file to a .csv file
def fits_to_csv(fits_file, csv_file):
    # Open the .fits file
    with fits.open(fits_file) as hdul:
        # Assuming the data is in the first extension (index 1) or primary HDU (index 0)
        data = hdul[1].data if len(hdul) > 1 else hdul[0].data
        
        # Convert the FITS data to a Pandas DataFrame
        df = pd.DataFrame(data)
        
        # Save the DataFrame to a CSV file
        df.to_csv(csv_file, index=False)
        print(f"Data successfully written to {csv_file}")
#getting the redshift out of vcosmic
def add_redshift_column(input_file, output_file):
    # Speed of light in km/s
    speed_of_light = 299792.458
    
    # Load the CSV file
    df = pd.read_csv(input_file)
    
    # Check if the "Vcosmic" column exists
    if 'Vcosmic' not in df.columns:
        raise ValueError("Column 'Vcosmic' not found in the input file")
    
    # Calculate the redshift and add it as a new column
    df['redshift'] = df['Vcosmic'] / speed_of_light
    
    # Replace negative redshift values with NaN
    df['redshift'] = df['redshift'].apply(lambda x: np.nan if x < 0 else x)

    # Round the redshift values to 3 decimal places
    df['redshift'] = df['redshift'].round(4)
    
    # Save the modified DataFrame to a new CSV file
    df.to_csv(output_file, index=False)

    print(f"File successfully written to {output_file}")