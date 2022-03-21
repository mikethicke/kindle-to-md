"""
Converts JSON Amazon Kindle notes generated by Bookcision to markdown.

Bookcision (https://bookcision.readwise.io/) is a bookmarklet that exports
Kindle notes and highlights (https://read.amazon.com/notebook). This script
converts notes and highlights exported as JSON to markdown.

Syntax: kindle-to-md <inputfile.json> <outputfile.md> 
"""

import sys
import json
import textwrap

def main() :
    """
    Main function for parsing Kindle JSON export to markdown.
    """
    try :
        ( input_filename, output_filename ) = parse_command_line_arguments()
        kindle_data = parse_json_file( input_filename )
        markdown_text = kindle_to_md( kindle_data )
        write_output( markdown_text, output_filename )
    except ( InvalidCommandLineArguments, MisformattedKindleData, FileNotFoundError ) as error :
        show_help( str( error ) )
        sys.exit(1)
    

def parse_command_line_arguments() -> tuple :
    """
    Parse the command line arguments and return as dict.

    Syntax: kindle-to-md <inputfile.json> [<outputfile.md>]

    Returns:
        A tuple with values for input_filename and output_filename. If the
        outputfile parameter is omitted, output_filename will be None.
    
    Raises:
        InvalidCommandLineArguments: There are too few or too many command line
        arguments.
    """
    if ( len( sys.argv ) < 2 or len( sys.argv ) > 3) :
        raise InvalidCommandLineArguments( "Incorrect number of command line arguments." )
    
    input_filename = sys.argv[1]
    if ( len( sys.argv ) == 3 ) :
        output_filename = sys.argv[2]
    else :
        output_filename = None
    
    return ( input_filename, output_filename )

def parse_json_file( file_name: str ) -> dict :
    """
    Parses json-encoded file and returns data object.

    Args:
        file_name: File name of the json file.
    
    Returns:
        Parsed data. For Kindle notes, will be a dict with entries as list in
        'highlights'.
    """
    with open( file_name, 'r' ) as file :
        try :
            data = json.load( file )
        except json.decoder.JSONDecodeError :
            raise MisformattedKindleData( "Input file is not a valid JSON document." )
    return data

def kindle_to_md ( kindle_data: dict, notes_section: bool = True ) -> str :
    """
    Translate data from Kindle export into MarkDown formatted string.

    Args:
        kindle_data: The Kindle notes and highlights data.
        notes_section: Whether to include a separate section for highlights with notes.
    
    Returns:
        Text formatted as MarkDown.
    """
    markdown_str = ''

    try :
        markdown_str += f"# {kindle_data['title']}\n\n"
        markdown_str += f"Authors: {kindle_data['authors']}\n\n"
    except KeyError :
        raise MisformattedKindleData( "Kindle export missing title or author fields." )

    if notes_section :
        markdown_str += "## Highlights with Notes\n\n"
        try :
            highlights_with_notes = [ i for i in kindle_data['highlights'] if i['note'] is not None ]
        except KeyError :
            raise MisformattedKindleData( "Kindle export missing expected fields." )
        for highlight in highlights_with_notes :    
            markdown_str += single_entry_to_md( highlight )
        markdown_str += "\n\n"

    markdown_str += "## All Highlights\n\n"
    for highlight in kindle_data['highlights'] :
        markdown_str += single_entry_to_md( highlight )

    return markdown_str

def single_entry_to_md( entry_data: dict ) -> str :
    """
    Translates a single entry into MarkDown.

    Args:
        entry_data: Data for a single entry
    
    Returns:
        MarkDown formatted string representing the entry.
    """
    markdown = ''

    try :
        kindle_link = f"[{entry_data['location']['value']}]({entry_data['location']['url']})"

        if entry_data['isNoteOnly'] and entry_data['text'] != '' :
            raise MisformattedKindleData

        if not entry_data['isNoteOnly'] and entry_data['text'] == '' :
            raise MisformattedKindleData
        
        if entry_data['isNoteOnly'] and entry_data['note'] and entry_data['note'] != '' :
            markdown += f"- Note: {entry_data['note']} ({kindle_link})\n"

        if not entry_data['isNoteOnly'] and entry_data['text'] != '' :
            markdown += f"- {entry_data['text']} ({kindle_link})\n"
            if entry_data['note'] and entry_data['note'] != '':
                markdown += f"    - Note: {entry_data['note']}\n"
    except KeyError :
        raise MisformattedKindleData( "Kindle export missing expeced fields." )

    return markdown

def write_output( output_text: str, filename: str | None ) :
    """
    Output MarkDown-formatted text.

    Args:
        output_text: The text to output.
        output_filename: File to write to, or None to output to stdout.
    """
    if filename is None :
        print ( output_text )
        return
    
    with open( filename, 'w' ) as file :
        file.write( output_text )

def show_help( help_message: str | None) :
    """
    Print help message.

    Args:
        help_message: If defined, a help message to output along with default help
    """
    if help_message is not None :
        print( help_message + "\n" )

    print ( textwrap.dedent('''\
        Converts JSON Amazon Kindle notes generated by Bookcision to markdown.

        Bookcision (https://bookcision.readwise.io/) is a bookmarklet that exports
        Kindle notes and highlights (https://read.amazon.com/notebook). This script
        converts notes and highlights exported as JSON to markdown.

        Syntax: kindle-to-md <inputfile.json> [<outputfile.md>]

        If outputfile is omitted, will be printed to stdout.
    ''') )

class InvalidCommandLineArguments( Exception ) :
    """
    Raised when command line arguments don't follow correct syntax.
    """

class MisformattedKindleData( Exception ) :
    """
    Raised when parsed Kindle JSON missing keys or contains unexpected data.
    """

if __name__ == '__main__' :
    main()
    
    
