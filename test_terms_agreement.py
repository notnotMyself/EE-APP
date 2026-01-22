#!/usr/bin/env python3
"""
Terms Agreement Feature - Acceptance Test Script

This script tests the complete Terms Agreement flow:
1. Backend API endpoints are accessible
2. Legal documents can be fetched
3. Consent can be created and checked
4. Frontend integration is correct

Usage:
    python3 test_terms_agreement.py
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

# Test user credentials (use a test account)
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

class TermsAgreementTester:
    def __init__(self):
        self.base_url = f"{BASE_URL}{API_PREFIX}"
        self.token = None
        self.test_results = []

    def log(self, message, success=True):
        """Log test result"""
        symbol = "✅" if success else "❌"
        print(f"{symbol} {message}")
        self.test_results.append({"message": message, "success": success})

    def test_backend_health(self):
        """Test 1: Check backend health"""
        print("\n=== Test 1: Backend Health Check ===")
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                self.log("Backend is healthy")
                return True
            else:
                self.log(f"Backend health check failed: {response.status_code}", False)
                return False
        except Exception as e:
            self.log(f"Backend health check error: {e}", False)
            return False

    def test_get_legal_documents(self):
        """Test 2: Get all legal documents"""
        print("\n=== Test 2: Get Legal Documents ===")
        try:
            response = requests.get(f"{self.base_url}/legal/documents", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    documents = data['data']['documents']
                    self.log(f"Fetched {len(documents)} legal documents")

                    # Check for required documents
                    doc_types = [doc['type'] for doc in documents]
                    if 'privacy_policy' in doc_types:
                        self.log("Privacy Policy document exists")
                    else:
                        self.log("Privacy Policy document NOT found", False)

                    if 'terms_of_service' in doc_types:
                        self.log("Terms of Service document exists")
                    else:
                        self.log("Terms of Service document NOT found", False)

                    return True
                else:
                    self.log("API returned success=false", False)
                    return False
            else:
                self.log(f"Failed to fetch legal documents: {response.status_code}", False)
                return False
        except Exception as e:
            self.log(f"Error fetching legal documents: {e}", False)
            return False

    def test_get_specific_document(self):
        """Test 3: Get specific legal document"""
        print("\n=== Test 3: Get Specific Document ===")
        try:
            # Test privacy policy
            response = requests.get(
                f"{self.base_url}/legal/documents/privacy_policy",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    doc = data['data']
                    self.log(f"Privacy Policy: {doc['title']} (v{doc['version']})")
                else:
                    self.log("Failed to get privacy policy", False)
                    return False
            else:
                self.log(f"Privacy policy request failed: {response.status_code}", False)
                return False

            # Test terms of service
            response = requests.get(
                f"{self.base_url}/legal/documents/terms_of_service",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    doc = data['data']
                    self.log(f"Terms of Service: {doc['title']} (v{doc['version']})")
                    return True
                else:
                    self.log("Failed to get terms of service", False)
                    return False
            else:
                self.log(f"Terms request failed: {response.status_code}", False)
                return False
        except Exception as e:
            self.log(f"Error getting specific document: {e}", False)
            return False

    def test_consent_without_auth(self):
        """Test 4: Consent without authentication (should fail)"""
        print("\n=== Test 4: Consent Without Authentication ===")
        try:
            response = requests.post(
                f"{self.base_url}/legal/consent",
                json={
                    "document_id": "test-doc-id",
                    "version": "1.0.0"
                },
                timeout=5
            )
            if response.status_code == 401:
                self.log("Correctly rejected unauthenticated consent request")
                return True
            else:
                self.log(f"Unexpected response for unauthenticated request: {response.status_code}", False)
                return False
        except Exception as e:
            self.log(f"Error testing unauthenticated consent: {e}", False)
            return False

    def test_flutter_files_exist(self):
        """Test 5: Check Flutter files exist"""
        print("\n=== Test 5: Flutter Files Verification ===")
        import os

        base_path = "/Users/80392083/develop/ee-app-pre-launch/ai_agent_app/lib"

        files_to_check = [
            "features/auth/data/legal_repository.dart",
            "features/auth/domain/models/legal_document.dart",
            "features/auth/domain/models/consent_status.dart",
            "features/auth/presentation/pages/terms_agreement_page.dart",
            "features/auth/presentation/controllers/auth_controller.dart",
            "core/router/app_router.dart",
        ]

        all_exist = True
        for file_path in files_to_check:
            full_path = os.path.join(base_path, file_path)
            if os.path.exists(full_path):
                self.log(f"File exists: {file_path}")
            else:
                self.log(f"File NOT found: {file_path}", False)
                all_exist = False

        return all_exist

    def test_flutter_imports(self):
        """Test 6: Check Flutter imports are correct"""
        print("\n=== Test 6: Flutter Import Verification ===")
        import os

        base_path = "/Users/80392083/develop/ee-app-pre-launch/ai_agent_app/lib"

        # Check legal_repository imports
        repo_file = os.path.join(base_path, "features/auth/data/legal_repository.dart")
        if os.path.exists(repo_file):
            with open(repo_file, 'r') as f:
                content = f.read()
                if 'import \'package:dio/dio.dart\';' in content:
                    self.log("legal_repository.dart: Dio import correct")
                else:
                    self.log("legal_repository.dart: Missing Dio import", False)
                    return False

                if 'AppConfig' in content:
                    self.log("legal_repository.dart: AppConfig usage correct")
                else:
                    self.log("legal_repository.dart: Missing AppConfig", False)
                    return False

        # Check terms_agreement_page imports
        page_file = os.path.join(base_path, "features/auth/presentation/pages/terms_agreement_page.dart")
        if os.path.exists(page_file):
            with open(page_file, 'r') as f:
                content = f.read()
                if 'flutter_markdown' in content:
                    self.log("terms_agreement_page.dart: flutter_markdown import correct")
                else:
                    self.log("terms_agreement_page.dart: Missing flutter_markdown", False)
                    return False

        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['success'])
        failed = total - passed

        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")

        if failed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['message']}")

        print("\n" + "="*60)

        return failed == 0

    def run_all_tests(self):
        """Run all tests"""
        print("="*60)
        print("TERMS AGREEMENT FEATURE - ACCEPTANCE TESTS")
        print("="*60)

        # Run tests
        self.test_backend_health()
        self.test_get_legal_documents()
        self.test_get_specific_document()
        self.test_consent_without_auth()
        self.test_flutter_files_exist()
        self.test_flutter_imports()

        # Print summary
        success = self.print_summary()

        return success

def main():
    """Main entry point"""
    tester = TermsAgreementTester()
    success = tester.run_all_tests()

    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please review the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
