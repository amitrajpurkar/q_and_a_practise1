#!/usr/bin/env python3
"""
CLI Main Entry Point for Q&A Practice Application.

This module provides the command-line interface for the Q&A practice application,
allowing users to interact with the application through terminal commands.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cli.commands import CLICommands
from src.utils.config import AppConfig
from src.utils.exceptions import QAAException


def setup_logging(verbose: bool = False) -> None:
    """
    Setup logging configuration for CLI.
    
    Args:
        verbose: Enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for CLI.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='qa-practice',
        description='Q&A Practice Application - Interactive CLI for topic-based learning',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Start interactive practice session
  %(prog)s --topic Physics           # Start with Physics topic
  %(prog)s --difficulty Hard         # Start with Hard difficulty
  %(prog)s --topic Math --easy       # Start Math practice with Easy difficulty
  %(prog)s --stats                   # Show application statistics
  %(prog)s --list-topics             # Show available topics
  %(prog)s --list-difficulties       # Show available difficulty levels
  %(prog)s --help                    # Show this help message
        """
    )
    
    # Topic selection
    parser.add_argument(
        '--topic', '-t',
        type=str,
        choices=['Physics', 'Chemistry', 'Math'],
        help='Select topic for practice session (Physics, Chemistry, Math)'
    )
    
    # Difficulty selection
    parser.add_argument(
        '--difficulty', '-d',
        type=str,
        choices=['Easy', 'Medium', 'Hard'],
        help='Select difficulty level (Easy, Medium, Hard)'
    )
    
    # Convenience flags for difficulty
    parser.add_argument(
        '--easy',
        action='store_const',
        const='Easy',
        dest='difficulty',
        help='Set difficulty to Easy'
    )
    
    parser.add_argument(
        '--medium',
        action='store_const',
        const='Medium',
        dest='difficulty',
        help='Set difficulty to Medium'
    )
    
    parser.add_argument(
        '--hard',
        action='store_const',
        const='Hard',
        dest='difficulty',
        help='Set difficulty to Hard'
    )
    
    # Information commands
    parser.add_argument(
        '--list-topics',
        action='store_true',
        help='List available topics and exit'
    )
    
    parser.add_argument(
        '--list-difficulties',
        action='store_true',
        help='List available difficulty levels and exit'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show application statistics and exit'
    )
    
    # Configuration
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--data-file',
        type=str,
        help='Path to questions CSV file'
    )
    
    # Output options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress non-error output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser


def validate_arguments(args: argparse.Namespace) -> None:
    """
    Validate command line arguments.
    
    Args:
        args: Parsed command line arguments
        
    Raises:
        Q&AApplicationError: If arguments are invalid
    """
    # Check for conflicting options
    if args.quiet and args.verbose:
        raise Q&AApplicationError("Cannot specify both --quiet and --verbose")
    
    # Check if information commands are combined with session parameters
    info_commands = [args.list_topics, args.list_difficulties, args.stats]
    if any(info_commands) and (args.topic or args.difficulty):
        raise Q&AApplicationError(
            "Information commands (--list-topics, --list-difficulties, --stats) "
            "cannot be combined with session parameters"
        )


def main() -> int:
    """
    Main entry point for CLI application.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Parse command line arguments
        parser = create_parser()
        args = parser.parse_args()
        
        # Validate arguments
        validate_arguments(args)
        
        # Setup logging
        setup_logging(verbose=args.verbose and not args.quiet)
        logger = logging.getLogger(__name__)
        
        # Load configuration
        config = AppConfig()
        if args.config:
            config.load_from_file(args.config)
        if args.data_file:
            config.data_file = args.data_file
        
        # Initialize CLI commands
        cli_commands = CLICommands(config)
        
        # Handle information commands
        if args.list_topics:
            cli_commands.list_topics()
            return 0
        
        if args.list_difficulties:
            cli_commands.list_difficulties()
            return 0
        
        if args.stats:
            cli_commands.show_statistics()
            return 0
        
        # Start practice session
        if not args.quiet:
            print("🎯 Q&A Practice Application")
            print("=" * 40)
        
        # Start interactive session or direct session
        if args.topic and args.difficulty:
            # Direct session with specified parameters
            cli_commands.start_session(topic=args.topic, difficulty=args.difficulty)
        elif args.topic or args.difficulty:
            # Partial parameters - prompt for missing ones
            cli_commands.start_session(topic=args.topic, difficulty=args.difficulty)
        else:
            # Fully interactive session
            cli_commands.interactive_session()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n👋 Session cancelled by user. Goodbye!")
        return 130
    except QAAException as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"❌ An unexpected error occurred. Use --verbose for details.", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
