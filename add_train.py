import csv

# Read the existing metadata.csv file
input_csv_file = 'album-mixed/metadata.csv'

# Create a temporary file to store the updated content
temp_csv_file = 'temp_metadata.csv'

with open(input_csv_file, 'r', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    header = reader.fieldnames

    # Create a temporary CSV file with the updated file names
    with open(temp_csv_file, 'w', newline='') as temp_csvfile:
        writer = csv.DictWriter(temp_csvfile, fieldnames=header)
        writer.writeheader()

        # Iterate through the rows and update the file names
        for row in reader:
            old_file_name = row.get('file_name', '')
            # Extract the numeric part of the file name
            index = old_file_name.find('_')
            if index != -1:
                numeric_part = old_file_name[index + 1:-4]
                new_file_name = f'train/train_{numeric_part}.png'
                row['file_name'] = new_file_name

            # Write the updated row to the temporary CSV file
            writer.writerow(row)

# Replace the existing metadata.csv file with the temporary file
import os
os.replace(temp_csv_file, input_csv_file)

print(f"File names in {input_csv_file} updated.")