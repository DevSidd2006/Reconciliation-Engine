#!/usr/bin/env python3
"""
Simple validation script for transaction data
No Unicode characters - ASCII only
"""

import json
import sys
from typing import Dict, List, Any, Optional


class SimpleValidator:
    """Basic validator for transaction data"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_transaction(self, transaction: Dict[str, Any]) -> bool:
        """Validate a single transaction record"""
        self.errors.clear()
        self.warnings.clear()
        
        # Check required fields
        required_fields = ['id', 'amount', 'currency', 'timestamp']
        for field in required_fields:
            if field not in transaction:
                self.errors.append(f"Missing required field: {field}")
        
        # Validate field types and values
        if 'id' in transaction:
            if not isinstance(transaction['id'], str) or not transaction['id'].strip():
                self.errors.append("Transaction ID must be a non-empty string")
        
        if 'amount' in transaction:
            try:
                amount = float(transaction['amount'])
                if amount <= 0:
                    self.errors.append("Amount must be positive")
            except (ValueError, TypeError):
                self.errors.append("Amount must be a valid number")
        
        if 'currency' in transaction:
            if not isinstance(transaction['currency'], str) or len(transaction['currency']) != 3:
                self.errors.append("Currency must be a 3-character string")
        
        if 'timestamp' in transaction:
            if not isinstance(transaction['timestamp'], (str, int)):
                self.errors.append("Timestamp must be string or integer")
        
        # Optional field validations
        if 'status' in transaction:
            valid_statuses = ['pending', 'completed', 'failed', 'cancelled']
            if transaction['status'] not in valid_statuses:
                self.warnings.append(f"Unknown status: {transaction['status']}")
        
        return len(self.errors) == 0
    
    def validate_batch(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a batch of transactions"""
        results = {
            'total': len(transactions),
            'valid': 0,
            'invalid': 0,
            'errors': [],
            'warnings': []
        }
        
        for i, transaction in enumerate(transactions):
            if self.validate_transaction(transaction):
                results['valid'] += 1
            else:
                results['invalid'] += 1
                results['errors'].append({
                    'index': i,
                    'transaction_id': transaction.get('id', 'unknown'),
                    'errors': self.errors.copy()
                })
            
            if self.warnings:
                results['warnings'].append({
                    'index': i,
                    'transaction_id': transaction.get('id', 'unknown'),
                    'warnings': self.warnings.copy()
                })
        
        return results
    
    def print_results(self, results: Dict[str, Any]) -> None:
        """Print validation results in a readable format"""
        print(f"Validation Results:")
        print(f"Total transactions: {results['total']}")
        print(f"Valid: {results['valid']}")
        print(f"Invalid: {results['invalid']}")
        
        if results['errors']:
            print("\nErrors found:")
            for error in results['errors']:
                print(f"  Transaction {error['index']} (ID: {error['transaction_id']}):")
                for err in error['errors']:
                    print(f"    - {err}")
        
        if results['warnings']:
            print("\nWarnings:")
            for warning in results['warnings']:
                print(f"  Transaction {warning['index']} (ID: {warning['transaction_id']}):")
                for warn in warning['warnings']:
                    print(f"    - {warn}")


def load_json_file(filepath: str) -> Optional[List[Dict[str, Any]]]:
    """Load transactions from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'transactions' in data:
                return data['transactions']
            else:
                print(f"Error: Expected list or object with 'transactions' key")
                return None
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file: {e}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


def main():
    """Main function to run validation"""
    if len(sys.argv) != 2:
        print("Usage: python simple_validation.py <json_file>")
        print("Example: python simple_validation.py transactions.json")
        sys.exit(1)
    
    filepath = sys.argv[1]
    transactions = load_json_file(filepath)
    
    if transactions is None:
        sys.exit(1)
    
    validator = SimpleValidator()
    results = validator.validate_batch(transactions)
    validator.print_results(results)
    
    # Exit with error code if any transactions are invalid
    if results['invalid'] > 0:
        sys.exit(1)
    else:
        print("\nAll transactions are valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()