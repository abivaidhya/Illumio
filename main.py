import csv
import re
from collections import defaultdict
import pdb

def load_lookup_table(lookup_file):
    """
    Loads the lookup table from a CSV file into a dictionary
    mapping (port, protocol) to the corresponding tags.
    The matching will be case-insensitive.
    """
    lookup_table = defaultdict(list)
    with open(lookup_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) != 3:  # Ensuring row 3 parts(dstport, protocol, tag)
                continue  # Skipping invalid rows
            try:
                dstport = int(row[0])  # Convert dstport to an integer
                protocol = row[1].strip().lower()  # Normalize protocol to lowercase
                tag = row[2].strip()  # The tag, also strip any excess whitespace
                lookup_table[(dstport, protocol)].append(tag)
            except ValueError:
                continue  # continue if dstport is not an int
    return lookup_table

def process_flow_logs(flow_log_file, lookup_table):
    """
    Processes the flow log file and returns the 
    counts of tags and port/protocol combinations.
    The matching will be case-insensitive.
    """
    tag_counts = defaultdict(int)
    port_protocol_counts = defaultdict(int)

    with open(flow_log_file, 'r') as file:
        for line in file:
            # Use regular expression to handle multiple spaces and tabs
            parts = re.split(r'\s+', line.strip())
            
            # Ensure the row has enough parts
            if len(parts) < 12:
                print(f"Skipping line (insufficient parts): {line.strip()}")
                continue

            try:
                dstport = int(parts[5])  # The dest port is in the 5th column (index 4)
                protocol_num = int(parts[7])  # The protocol is in the 8th column (index 7)

                # Map protocol numbers to protocol names and 
                # names not present, map it other
                if protocol_num == 6:
                    protocol = 'tcp'
                elif protocol_num == 17:
                    protocol = 'udp'
                else:
                    protocol = 'other'

                # Convert flow data to lowercase to cover the case-insensitive req
                protocol = protocol.lower()

                # Get the corresponding tags from the lookup table
                tag = lookup_table.get((dstport, protocol), None)

                if tag:
                    # If tags are found, update the counts
                    for t in tag:
                        tag_counts[t] += 1
                else:
                    # If no tag is found, count as "Untagged"
                    tag_counts['Untagged'] += 1
                
                # Track the port/protocol combination count
                port_protocol_counts[(dstport, protocol)] += 1

            except ValueError as e:
                print(f"Skipping line due to error: {line.strip()} - Error: {e}")

    return tag_counts, port_protocol_counts

def write_output(tag_cts, port_protocol_counts, op_file):
    """
    Writes the tag counts and port/protocol counts to the output file.
    """
    with open(op_file, 'w') as file:
        file.write("Tag Counts:\n")
        file.write("Tag,Count\n")
        for tag, ct in tag_cts.items():
            file.write(f"{tag},{ct}\n")

        file.write("\nPort/Protocol Combination Counts:\n")
        file.write("Port,Protocol,Count\n")
        for (port, protocol), count in port_protocol_counts.items():
            file.write(f"{port},{protocol},{count}\n")

def main(flow_log_file, lookup_file, output_file):
    lookup_table = load_lookup_table(lookup_file)
    tag_counts, port_protocol_counts = process_flow_logs(flow_log_file, lookup_table)
    write_output(tag_counts, port_protocol_counts, output_file)
    print(f"Output written to {output_file}")

if __name__ == "__main__":
    flow_log_file = "flow_logs.txt"  # Input file containing flow logs
    lookup_file = "lookup_table.csv"  # Input file containing the lookup table
    output_file = "output.csv"  # Output file containing the results
    
    main(flow_log_file, lookup_file, output_file)