from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
import PyPDF2

class PDFViewsTest(APITestCase):
    
    def setUp(self):
        """Setup test user and get authentication tokens"""
        self.user = User.objects.create_user(username="testuser", password="password123")
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_register_user(self):
        """Test user registration"""
        response = self.client.post('/api/register/', {'username': 'newuser', 'password': 'password123'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_user(self):
        """Test user login"""
        response = self.client.post('/api/login/', {'username': 'testuser', 'password': 'password123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.json())

    def test_text_to_pdf(self):
        """Test converting text to PDF"""
        response = self.client.post('/api/text-to-pdf/', {'text': 'Hello, World!'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="converted.pdf"')

    def test_merge_pdfs(self):
        """Test merging two PDFs"""
        pdf_content = BytesIO()
        writer = PyPDF2.PdfWriter()
        writer.add_blank_page(width=300, height=300)
        writer.write(pdf_content)
        pdf_content.seek(0)

        pdf1 = SimpleUploadedFile("file1.pdf", pdf_content.read(), content_type="application/pdf")
        pdf2 = SimpleUploadedFile("file2.pdf", pdf_content.read(), content_type="application/pdf")

        response = self.client.post('/api/merge-pdfs/', {'pdfs': [pdf1, pdf2]}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="merged.pdf"')

    def test_pdf_to_word(self):
        """Test converting PDF to Word"""
        pdf_content = BytesIO()
        writer = PyPDF2.PdfWriter()
        writer.add_blank_page(width=300, height=300)
        writer.write(pdf_content)
        pdf_content.seek(0)

        pdf_file = SimpleUploadedFile("test.pdf", pdf_content.read(), content_type="application/pdf")

        response = self.client.post('/api/pdf-to-word/', {'pdf': pdf_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="converted.docx"')

    def test_highlight_pdf(self):
        """Test highlighting text in a PDF"""
        pdf_content = BytesIO()
        writer = PyPDF2.PdfWriter()
        writer.add_blank_page(width=300, height=300)
        writer.write(pdf_content)
        pdf_content.seek(0)

        pdf_file = SimpleUploadedFile("test.pdf", pdf_content.read(), content_type="application/pdf")

        response = self.client.post('/api/highlight-pdf/', {'pdf': pdf_file, 'text': 'Test'}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="highlighted.pdf"')

    def test_get_history(self):
        """Test fetching user history"""
        response = self.client.get('/api/get-history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('history', response.json())
