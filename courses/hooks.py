# from paypal.standard.models import ST_PP_COMPLETED
# from paypal.standard.ipn.signals import valid_ipn_received	

# def payment_success_hook(sender, **kwargs):
# 	ipn_object = sender

# 	print('IPN RECEIVED')

# 	if ipn_object.payment_status == ST_PP_COMPLETED:
# 		if ipn_object.receiver_email != "edubin@gmail.com":
# 			return
# 	else:
# 		pass
	
# 	print(sender)
# 	return

# valid_ipn_received.connect(payment_success_hook)