import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import json
import logging

class VacuumLogic(beam.DoFn):
    """
    Osipov Pattern: VACUUM (Valid, Accurate, Consistent, Uniform, Unified).
    Filters out invalid or anomalous records.
    """
    def process(self, element):
        try:
            # element is a list from CSV reader
            vendor_id = int(element[0])
            trip_distance = float(element[4])
            fare_amount = float(element[5])

            # Data Quality Gates (Phase 0111, 0112, 0113)
            if trip_distance <= 0 or fare_amount < 2.50:
                logging.info(f"Filtering invalid record: {element}")
                return

            # Outlier Detection (Phase 0114)
            if trip_distance > 100 or fare_amount > 500:
                logging.warning(f"Filtering outlier: {element}")
                return

            yield {
                "vendor_id": vendor_id,
                "pickup_datetime": element[1],
                "dropoff_datetime": element[2],
                "passenger_count": int(element[3]),
                "trip_distance": trip_distance,
                "fare_amount": fare_amount
            }
        except (ValueError, IndexError) as e:
            logging.error(f"Error processing element {element}: {str(e)}")

def run_etl(input_path, output_path):
    options = PipelineOptions()
    with beam.Pipeline(options=options) as p:
        (
            p 
            | "Read CSV" >> beam.io.ReadFromText(input_path, skip_header_lines=1)
            | "Parse CSV" >> beam.Map(lambda line: line.split(","))
            | "Apply VACUUM" >> beam.ParDo(VacuumLogic())
            | "Write Parquet" >> beam.io.WriteToParquet(
                output_path,
                pyarrow_schema=None, # Schema discovery enabled
                file_name_suffix=".parquet"
            )
        )

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    logging.getLogger().setLevel(logging.INFO)
    run_etl(args.input, args.output)
