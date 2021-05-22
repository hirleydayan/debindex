#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime
from gzip import BadGzipFile
from io import BytesIO
from typing import Union

import click
import pandas as pd
import requests
from requests.exceptions import InvalidURL

logging.basicConfig(format='%(asctime)s :: %(levelname).1s :: %(name)s :: %(message)s', level=logging.INFO)
_logger = logging.getLogger(os.path.basename(__file__))


@click.command(options_metavar='<options>')
@click.help_option('-h', '--help')
@click.option('-b', '--baseurl',
              type=str,
              help='Base debian mirror URL',
              default='http://ftp.uk.debian.org/debian/dists/stable/main',
              metavar='<url>',
              show_default=True)
@click.option('-d', '--download',
              is_flag=True,
              default=False,
              show_default=True,
              help='Download index file from remote URL')
@click.option('-l', '--log_level',
              default='info',
              type=click.Choice(['info', 'warning', 'error', 'critical']),
              metavar='<level>',
              show_default=True,
              help='Logging level')
@click.option('-o', '--output',
              default=None,
              metavar='<filename>',
              help='Optional output file. If not specified, the output is printed on stdout.')
@click.option('-n', '--number_of_elements',
              default=10,
              type=int,
              metavar='<number>',
              help='Number of elements to be printed on stdout')
@click.argument('architecture', required=1, metavar='<architecture>')
def main(baseurl: str, architecture: str, download: bool, log_level: str, output: str, number_of_elements: int) -> None:
    """
    Command for extracting the number of entries per package from the Debian index file, from the selected
    repository and architecture.
    """
    _logger.setLevel(log_level.upper())
    print(f'Debian Index Statistics Tool "{os.path.basename(__file__)}"')
    index_file_name = f'Contents-{architecture}.gz'                        # Define index name with entered architecture
    baseurl = baseurl.strip()                                              # Remove extra spaces
    index_file_url = f'{baseurl.rstrip("/")}/{index_file_name}'            # Define full URL to index file
    try:
        if download:                                                       # if download command switch is entered
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")           # Use system timestamp in file name
            download_file_name = index_file_name.split('.')                # Add timestamp to the downloaded file
            download_file_name.insert(-1, timestamp)                       # name
            download_file_name = '.'.join(download_file_name)              # Construct file name with all strings
            download_index(index_file_url, download_file_name)             # Call function for downloading index file
            df = read_index_local(download_file_name,                      # Read local downloaded file
                                  column_names=('filename', 'package'))
        else:                                                              # if download switch is not entered (default)
            df = read_index_remote(index_file_url,                         # Read remote file if download parameter
                                   column_names=('filename', 'package'))   # not entered
        df_result = count_occurrences(df, ('package',))                    # Call function for counting the occurrences
        output_result(df_result, output, number_of_elements)               # Call function for outputting the result
    except InvalidURL:
        _logger.error(f'Invalid URL "{baseurl}"')                          # Print error if URL is invalid
    except BadGzipFile:
        _logger.error('Could not read index file')                         # Print error if GZIP file is invalid
    except KeyboardInterrupt:
        _logger.info('Canceled by user.')
    print('Finished.')


def download_index(url: str, output_file_name: str) -> None:
    """
    Function for downloading the gzipped index file locally
    :param url: the index file URL string
    :param output_file_name: the output file name
    """
    _logger.info(f'Downloading index file from "{url}" ...')
    r = requests.get(url)                                                  # Define request to index file in remote URL
    open(f'{output_file_name}', 'wb').write(r.content)                     # Write locally the binary gzip file
    _logger.info(f'Downloading finished.')


def read_index_remote(url: str, column_names: Union[tuple, list]) -> pd.DataFrame:
    """
    Read remote index file from URL
    :param url: the index file URL string
    :param column_names: the dataframe column names list
    :return: the dataframe with extracted data from index file
    """
    _logger.info(f'Reading index file from "{url}" ...')
    s = requests.get(url).content                                          # Define request to index file in remote URL
    df = _read_csv(BytesIO(s), column_names)                               # Call read function passing binary stream
    _logger.info(f'Reading finished.')
    return df


def read_index_local(file_path: str, column_names: Union[tuple, list]) -> pd.DataFrame:
    """
    Read local index file from path
    :param file_path: the index file path string
    :param column_names: the dataframe column names list
    :return: the dataframe with extracted data from index file
    """
    _logger.info(f'Reading index file from local file "{file_path}" ...')
    df = _read_csv(file_path, column_names)                               # Call read function passing local file path
    _logger.info(f'Reading finished.')
    return df


def _read_csv(data: Union[str, BytesIO], column_names: Union[tuple, list], sep: str = '\\s+') -> pd.DataFrame:
    """
    Helper private function from reading csv
    """
    df = pd.read_csv(data, compression='gzip', names=['column'])          # Read CSV and create a dataframe
    df = df.iloc[:, 0].str.split(sep, 1, expand=True)                     # Split dataframe in 2 columns by first space
    df.columns = column_names                                             # Name the columns
    return df


def count_occurrences(df: pd.DataFrame, index: Union[tuple, list]) -> pd.DataFrame:
    """
    Function for counting the number of occurrences per package in the index file and sorting the result
    :param df: the dataframe
    :param index: the index for counting the number of occurrences
    :return: the dataframe with the sorted counting of entries per package
    """
    _logger.info(f'Counting index entries occurrences ...')
    df_pivoted = df.pivot_table(index=index, aggfunc='size')              # Create pivot datatable counting the entries
    df_pivoted = df_pivoted.reindex(df_pivoted.sort_values(ascending=False).index)  # Sort datatable in descending order
    _logger.info(f'Counting finished.')
    return df_pivoted


def output_result(df: pd.DataFrame, file_path: str, number_of_elements=10) -> None:
    """
    Function for outputting the result into a CSV file or on stdout.
    :param df: the dataframe to be output
    :param file_path: the file name for saving the dataframe. If not defined, the dataframe is printed on stdout.
    :param number_of_elements: the number of element to be printed on stdout from the input dataframe
    """
    if df is None:
        return
    if file_path is not None:                                             # If a output file is defined, save result
        _logger.info(f'Saving result to "{file_path}" ...')
        df.to_csv(file_path, index=True, header=False)                    # Save result into a file using CSV format
        _logger.info(f'Saving finished.')
    else:                                                                 # If output file is not defined, print result
        print('------------------------------------------------------------------------------')
        print(f'  Top {number_of_elements} packages with more files associated:')
        print('------------------------------------------------------------------------------')
        print(df.head(number_of_elements).to_string(header=False))
        print('------------------------------------------------------------------------------')


if __name__ == '__main__':
    main()
