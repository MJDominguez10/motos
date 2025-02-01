import dealerships
import merge

if __name__ == "__main__":
    print()
    print("######## Analysing dealerships ############# ")
    input_folder = "/Users/monkiky/Desktop/motos_collect/autotrader_raw_data/"
    output_folder = "/Users/monkiky/Desktop/motos_collect/data2plot/Dealerships/"
    dealerships.dealerships(input_folder, output_folder)
    print()

    print("######## Analysing motorbikes ######## ")
    # Define your folder path and output file name
    data_folder = "/Users/monkiky/Desktop/motos_collect/autotrader_raw_data/"
    output_filename = "/Users/monkiky/Desktop/motos_collect/data2plot/cleaned_autotrader_data.csv"

    # Call the function to process the data
    merge.merge(data_folder, output_filename)