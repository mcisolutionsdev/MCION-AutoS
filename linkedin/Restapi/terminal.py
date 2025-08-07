import webbrowser
import requests
import secrets
import jwt
import json

import base64
import hashlib

import sys

from urllib.parse import urlparse, parse_qs

CLIENT_ID = "78s4xqz0muybqy"
CLIENT_SECRET = "WPL_AP1.VrZlxpQdy1xgY5Np.fLuhNA=="
REDIRECT_URI = "http://localhost:3000/callback"

AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
AUTHORIZATION_URL_PKCE = "https://www.linkedin.com/oauth/native-pkce/authorization"

TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

POST_URL = 'https://api.linkedin.com/v2/ugcPosts'
REGISTER_UPLOAD_URL = 'https://api.linkedin.com/v2/assets?action=registerUpload'

def generate_auth_url():
    state = secrets.token_hex( 16 ) # Random state for CSRF protection

    # Store the state securely (in a real application, you might write to a file or use another method)
    print( f"Generated state: { state }" )
    print( "Store this state value securely to verify when LinkedIn redirects back" )
    
    # Build authentication URL with w_member_social scope
    auth_url = f"{ AUTHORIZATION_URL }?" \
        "response_type=code&" \
        f"client_id={ CLIENT_ID }&" \
        f"redirect_uri={ REDIRECT_URI }&" \
        f"state={ state }&" \
        "scope=w_member_social openid profile email"
    
    return auth_url, state

def generate_code_verifier():
    """Generate random code_verifier on PKCE request"""

    return secrets.token_urlsafe( 64 ) # A random URL-safe string (43 to 128 characters long)

def generate_code_challenge( verifier ):
    """Create code_challenge from code_verifier using S256 method"""

    # Hash code_verifier with SHA256
    sha256_hash = hashlib.sha256( verifier.encode() ).digest()
    # Encode hash into base64url
    base64url_encoded = base64.urlsafe_b64encode( sha256_hash ).decode( 'utf-8' )
    # Remove padding '=' according to base64url standard
    return base64url_encoded.rstrip( '=' )

def generate_pkce_auth_url():
    state = secrets.token_hex( 16 ) # Random state for CSRF protection

    # Create code_verifier and code_challenge for PKCE
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge( code_verifier )
    
    # Store the state securely (in a real application, you might write to a file or use another method)
    print( f"Generated state: { state }" )
    print( f"Generated code_verifier: { code_verifier }" )
    print( "Store this state value securely to verify when LinkedIn redirects back" )
    
    auth_url = f"{ AUTHORIZATION_URL_PKCE }?" \
        "response_type=code&" \
        f"client_id={ CLIENT_ID }&" \
        f"redirect_uri={ REDIRECT_URI }&" \
        f"state={ state }&" \
        f"code_challenge={ code_challenge }&" \
        "code_challenge_method=S256&" \
        "scope=w_member_social"
    
    return auth_url, state, code_verifier

def process_callback_url( callback_url, stored_state ):
    try:
        # Get query part from URL
        parsed_url = urlparse( callback_url )
        query_params = parse_qs( parsed_url.query )
        
        auth_code = query_params.get( 'code', [ None ] )[ 0 ]
        received_state = query_params.get( 'state', [ None ] )[ 0 ]
        
        if not auth_code:
            print( "Error: Authentication token not found in URL" )
            
            return None
        
        if received_state != stored_state:
            print( "Warning: State does not match! Possible CSRF attack" )
            choice = input( "Do you want to continue? (y/n): " )
            
            if choice.lower() != 'y':
                return None
        
        # Exchange authentication code for access token
        token_payload = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        
        print( "\nExchanging authentication code for access token..." )
        token_response = requests.post( TOKEN_URL, data=token_payload )

        status_code = token_response.status_code
        token_response = token_response.json()
        print( "Response: ", json.dumps( token_response, indent=2 ) )
        
        if status_code == 200:
            return token_response
        
        return None
        
    except Exception as e:
        print( f"Error processing callback URL: { str( e ) }" )
    
def decode_id_token( id_token ):
    """
    Decode the ID token to extract user information
    
    Args:
        id_token (str): ID token from LinkedIn OAuth with OpenID Connect
        
    Returns:
        tuple: (success_flag, member_id, user_info_dict)
    """
    try:
        print( "Decoding ID token to extract user information..." )
            
        # Decode the token without verifying signature
        decoded_token = jwt.decode( id_token, options={ "verify_signature": False } )
        
        # Extract user information
        user_info = {
            "id": decoded_token.get( 'sub' ),
            "name": decoded_token.get( 'name' ),
            "email": decoded_token.get( 'email' ),
            "picture": decoded_token.get( 'picture' ),
            "given_name": decoded_token.get( 'given_name' ),
            "family_name": decoded_token.get( 'family_name' )
        }
        
        # Display user information
        print( "User information from ID token:" )
        print( f"ID (sub): { user_info[ 'id' ] }" )
        print( f"Name: { user_info[ 'name' ] }" )
        print( f"Email: { user_info[ 'email' ] }" )
        
        return user_info
            
    except Exception as e:
        print( f"Error decoding ID token: { str( e ) }" )
        return None

def create_linkedin_post( access_token, id_token, post_content ):
    """
    Tạo một bài đăng văn bản đơn giản trên LinkedIn sử dụng thông tin từ ID token
    
    Args:
        access_token (str): Access token của LinkedIn
        id_token (str): ID token từ OAuth với OpenID Connect
        post_content (str): Nội dung bài đăng
        
    Returns:
        dict: Kết quả từ API LinkedIn
    """
    # Bước 1: Giải mã ID token để lấy thông tin người dùng
    # try:
    #     print("Đang giải mã ID token để lấy thông tin người dùng...")
    #     decoded_token = jwt.decode( id_token, options={ "verify_signature": False } )
        
    #     # Hiển thị thông tin người dùng từ ID token
    #     print("Thông tin người dùng từ ID token:")
    #     print(f"ID (sub): {decoded_token.get('sub')}")
    #     print(f"Tên: {decoded_token.get('name')}")
    #     print(f"Email: {decoded_token.get('email')}")
        
    #     # Kiểm tra xem có ID người dùng (sub) không
    #     member_id = decoded_token.get('sub')
    #     if not member_id:
    #         print("Không tìm thấy ID người dùng trong ID token.")
    #         # Trong trường hợp này, chúng ta sẽ sử dụng cách làm việc thay thế
    #         member_id = None
    # except Exception as e:
    #     print(f"Lỗi khi giải mã ID token: {str(e)}")

    #     return None

    user_info = decode_id_token( id_token )
    if not user_info:
        return None
    
    # Prepare data
    member_id = user_info[ 'id' ]
    post_data = {
        "author": f"urn:li:person:{ member_id }",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post_content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    print( "Creating post..." )
    print( f"Author URN: { post_data[ 'author' ] }" )
    
    post_headers = {
        'Authorization': f'Bearer { access_token }',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    # Perform request
    post_response = requests.post(
        POST_URL, 
        headers=post_headers, 
        json=post_data
    )
    
    # Kiểm tra kết quả
    if post_response.status_code == 201:
        print( "Bài đăng đã được tạo thành công!" )
        return post_response.json()
    else:
        print(f"Lỗi khi tạo bài đăng: {post_response.status_code} - {post_response.text}")
        return None

def create_linkedin_post_with_image(access_token, id_token, post_content, image_url, image_title="Hình ảnh"):
    """
    Tạo một bài đăng với hình ảnh trên LinkedIn sử dụng thông tin từ ID token
    
    Args:
        access_token (str): Access token của LinkedIn
        id_token (str): ID token từ OAuth với OpenID Connect
        post_content (str): Nội dung bài đăng
        image_url (str): URL của hình ảnh
        image_title (str): Tiêu đề của hình ảnh
        
    Returns:
        dict: Kết quả từ API LinkedIn
    """
    # Bước 1: Giải mã ID token để lấy thông tin người dùng
    # try:
    #     print("Đang giải mã ID token để lấy thông tin người dùng...")
    #     decoded_token = jwt.decode(id_token, options={"verify_signature": False})
        
    #     # Hiển thị thông tin người dùng từ ID token
    #     print("Thông tin người dùng từ ID token:")
    #     print(f"ID (sub): {decoded_token.get('sub')}")
    #     print(f"Tên: {decoded_token.get('name')}")
    #     print(f"Email: {decoded_token.get('email')}")
        
    #     # Kiểm tra xem có ID người dùng (sub) không
    #     member_id = decoded_token.get('sub')
    #     if not member_id:
    #         print("Không tìm thấy ID người dùng trong ID token.")
    #         member_id = None
    # except Exception as e:
    #     print(f"Lỗi khi giải mã ID token: {str(e)}")
    #     print("Sẽ thử sử dụng phương pháp thay thế...")
    #     member_id = None

    user_info = decode_id_token( id_token )
    if not user_info:
        return None
    
    member_id = user_info[ 'id' ]
    author_urn = f"urn:li:person:{ member_id }"
    print( f"Author URN: { author_urn }" )
    
    # Bước 3: Đăng ký asset (hình ảnh) trước khi đăng bài
    register_upload_url = 'https://api.linkedin.com/v2/assets?action=registerUpload'
    register_upload_data = {
        "registerUploadRequest": {
            "recipes": [
                "urn:li:digitalmediaRecipe:feedshare-image"
            ],
            "owner": author_urn,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    print("Đang đăng ký upload hình ảnh...")
    register_response = requests.post(
        register_upload_url,
        headers=headers,
        json=register_upload_data
    )
    
    if register_response.status_code != 200:
        print(f"Lỗi khi đăng ký upload: {register_response.status_code} - {register_response.text}")
        return None
    
    # Phân tích thông tin từ phản hồi đăng ký
    register_data = register_response.json()
    asset_id = register_data.get('value', {}).get('asset')
    upload_url = register_data.get('value', {}).get('uploadMechanism', {}).get('com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest', {}).get('uploadUrl')
    
    if not asset_id or not upload_url:
        print("Không thể lấy thông tin upload từ phản hồi")
        return None
    
    # Bước 4: Tải hình ảnh từ URL và upload lên LinkedIn
    print("Đang tải hình ảnh từ URL...")
    image_response = requests.get(image_url)
    
    if image_response.status_code != 200:
        print(f"Lỗi khi tải hình ảnh: {image_response.status_code}")
        return None
    
    image_data = image_response.content
    
    print("Đang upload hình ảnh lên LinkedIn...")
    upload_response = requests.put(
        upload_url,
        data=image_data,
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )
    
    if upload_response.status_code not in (200, 201):
        print(f"Lỗi khi upload hình ảnh: {upload_response.status_code} - {upload_response.text}")
        return None
    
    # Bước 5: Tạo bài đăng với hình ảnh đã upload
    post_data = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post_content
                },
                "shareMediaCategory": "IMAGE",
                "media": [
                    {
                        "status": "READY",
                        "description": {
                            "text": image_title
                        },
                        "media": asset_id,
                        "title": {
                            "text": image_title
                        }
                    }
                ]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    print("Đang tạo bài đăng với hình ảnh...")
    post_response = requests.post(
        POST_URL,
        headers=headers,
        json=post_data
    )
    
    if post_response.status_code in (200, 201):
        print("Bài đăng với hình ảnh đã được tạo thành công!")
        return post_response.json()
    else:
        print(f"Lỗi khi tạo bài đăng: {post_response.status_code} - {post_response.text}")
        return None

if __name__ == "__main__":
    # Generate the authentication URL
    auth_url, state = generate_auth_url()
    
    # auth_url, state, code_verifier = generate_pkce_auth_url()
    
    # Print URL for reference
    print( "\nOpening LinkedIn authentication URL in browser..." )
    print( f"URL: { auth_url }" )
    
    # Open URL in the default web browser
    webbrowser.open( auth_url )

    # User guide
    print( "\nLưu ý quan trọng:" )
    print( "1. Đăng nhập vào LinkedIn và cho phép ứng dụng truy cập" )
    print( "2. Sau khi xác thực, LinkedIn sẽ chuyển hướng đến một URL bắt đầu với:", REDIRECT_URI )
    print( "3. URL này sẽ chứa tham số 'code' và 'state'" )
    print( f"4. Kiểm tra tham số 'state' phải bằng: { state }" )
    
    # Đợi người dùng nhập URL callback
    print( "\nSau khi xác thực, hãy sao chép toàn bộ URL chuyển hướng và dán vào đây:" )
    callback_url = input( "> " ).strip()
    
    token_data = process_callback_url( callback_url, state )
    if token_data is None:
        sys.exit( 1 )

    access_token = token_data[ 'access_token' ]
    id_token = token_data[ 'id_token' ]

    # Chọn loại bài đăng
    post_type = input("Bạn muốn đăng bài với hình ảnh không? (y/n): ").lower()
    
    # Nhập nội dung bài đăng
    post_content = input("Nhập nội dung bài đăng: ")
    
    if post_type == 'y':
        # Đăng bài với hình ảnh
        image_url = input("Nhập URL của hình ảnh: ")
        image_title = input("Nhập tiêu đề của hình ảnh (để trống nếu không cần): ") or "Hình ảnh"
        
        result = create_linkedin_post_with_image(access_token, id_token, post_content, image_url, image_title)
    else:
        # Đăng bài văn bản đơn giản
        result = create_linkedin_post(access_token, id_token, post_content)
    
    if result:
        print( "Result: ", json.dumps( result, indent=2 ) )
    else:
        print( "Cannot create post." )
    