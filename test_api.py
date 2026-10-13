from app import app, init_db

def test():
    # Ensure fresh DB initialized
    init_db(reset_products=False)
    client = app.test_client()
    
    # 1. Test Products
    r1 = client.get('/api/products')
    assert r1.status_code == 200
    print("[OK] Products API: retrieved", len(r1.json['data']), "Pakistani medicines")

    # 2. Test Order Creation (Kot Sultan, Layyah) & Dual Notification (Admin Panel + Gmail)
    payload = {
        'customer_name': 'Tariq Mehmood',
        'customer_phone': '0300-7788990',
        'customer_email': 'tariq@kotsultan.pk',
        'city': 'Kot Sultan, Layyah',
        'address': 'Railway Road, Kot Sultan',
        'payment_method': 'JazzCash / Easypaisa (03095518882)',
        'items': [
            {'id': 1, 'name': 'Panadol 500mg Tablets', 'price': 58.0, 'quantity': 1},
            {'id': 5, 'name': 'Brufen 400mg Tablets', 'price': 125.0, 'quantity': 2}
        ],
        'subtotal': 308.0,
        'discount': 0.0
    }
    r2 = client.post('/api/orders', json=payload)
    assert r2.status_code == 201
    order_id = r2.json['order_id']
    assert 'admin_wa_url' in r2.json
    assert r2.json['admin_gmail'] == 'hammadfareed876@gmail.com'
    assert 'admin_gmail_compose_url' in r2.json
    print("[OK] Order Creation API: generated Order ID:", order_id)
    print("[OK] Admin Instant Alert generated for Admin: 03045518658")
    print("[OK] Admin Gmail Notification generated for: hammadfareed876@gmail.com")

    # 3. Test Admin Login for 03045518658
    r_login = client.post('/api/admin/login', json={'phone': '03045518658', 'pin': '7860'})
    assert r_login.status_code == 200
    token = r_login.json['token']
    print("[OK] Admin Login: Successfully authenticated for 03045518658!")

    # 4. Test Admin Email Logs API
    r_emails = client.get('/api/admin/emails', headers={'Authorization': f'Bearer {token}'})
    assert r_emails.status_code == 200
    email_logs = r_emails.json['data']
    assert len(email_logs) > 0
    assert email_logs[0]['to_email'] == 'hammadfareed876@gmail.com'
    assert order_id in email_logs[0]['subject']
    print("[OK] Admin Email Logs API: verified dispatch to hammadfareed876@gmail.com!")

    # 5. Test Admin Settings API
    r_settings = client.get('/api/admin/settings', headers={'Authorization': f'Bearer {token}'})
    assert r_settings.status_code == 200
    assert r_settings.json['admin_gmail'] == 'hammadfareed876@gmail.com'
    print("[OK] Admin Settings API: retrieved admin_gmail:", r_settings.json['admin_gmail'])

    # 6. Test 12-Hour Pending Reminders API
    r_reminders = client.get('/api/admin/pending_reminders?simulate=1', headers={'Authorization': f'Bearer {token}'})
    assert r_reminders.status_code == 200
    assert 'overdue_orders' in r_reminders.json
    print("[OK] 12-Hour Pending Reminders API: tracked", r_reminders.json['count'], "overdue orders with reminders!")

    # 7. Test Admin Alerts API
    r_alerts = client.get('/api/admin/alerts', headers={'Authorization': f'Bearer {token}'})
    assert r_alerts.status_code == 200
    print("[OK] Admin Alerts API: retrieved", len(r_alerts.json['alerts']), "instant alerts!")

    # 8. Test Admin Updating Status to Verified (with rich customer notification including product names)
    r_status = client.post(f'/api/admin/orders/{order_id}/status', headers={'Authorization': f'Bearer {token}'}, json={'status': 'Verified by Pharmacist'})
    assert r_status.status_code == 200
    assert 'wa_notify_url' in r_status.json
    notif_text = r_status.json['notification_text']
    assert 'Panadol 500mg Tablets' in notif_text
    assert 'Brufen 400mg Tablets' in notif_text
    assert 'Railway Road, Kot Sultan' in notif_text
    assert '03095518882' in notif_text
    print("[OK] Admin Order Verification: customer notification created with complete product names & order info!")

    # 9. Test Customer Notifications API
    r_notif = client.get(f'/api/orders/{order_id}/notifications')
    assert r_notif.status_code == 200
    assert r_notif.json['current_status'] == 'Verified by Pharmacist'
    cust_notifs = r_notif.json['notifications']
    assert len(cust_notifs) > 0
    assert 'Panadol 500mg Tablets' in cust_notifs[0]['message']
    print("[OK] Customer Notifications: verified live status and product names breakdown!")

    print("\n=======================================================")
    print(" ALL 9 COMPREHENSIVE TESTS PASSED WITH 100% SUCCESS!  ")
    print("=======================================================")

if __name__ == '__main__':
    test()
