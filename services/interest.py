from django.db.models import F, Max, Subquery
from django.shortcuts import get_object_or_404
from wallet.models import UserWallet 
from shares.models import Shares
from interest.models import InterestEarned


def update_interest_earned(loan_repayment):
    loan = loan_repayment.loan
    user = loan.borrower
    user_data = users_in_same_wallet(user)
    interest_rate = loan.interest_rate
    loan_amount = loan.amount_borrowed

    # Calculate interest amount outside the loop
    interest_amount = (loan_amount * interest_rate) / 100

    # Pre-fetch all user wallet details and map them
    user_ids = [user['user'].id for user in user_data]
    user_wallets = UserWallet.objects.filter(user_id__in=user_ids)
    user_wallet_map = {wallet.user_id: wallet for wallet in user_wallets}

    # # Pre-fetch all users' latest shares
    # latest_shares = Shares.objects.filter(
    #     user_id__in=user_ids
    # ).order_by('user_id', '-timestamp').distinct('user_id')

        # Step 1: Annotate each user with their latest share's timestamp
    latest_timestamps = Shares.objects.filter(
        user_id__in=user_ids
    ).values('user_id').annotate(
        latest_timestamp=Max('timestamp')
    ).values('latest_timestamp')

    # Step 2: Filter the shares to get the ones with the latest timestamps
    latest_shares = Shares.objects.filter(
        timestamp__in=Subquery(latest_timestamps)
    )

    latest_share_map = {share.user_id: share for share in latest_shares}

    # Prepare bulk operations
    interest_earned_records = []

    for user in user_data:
        user_id = user['user'].id
        latest_share = latest_share_map.get(user_id)
        if latest_share:
            interest_earned_amount = (interest_amount * latest_share.share_percentage) / 100
            user_wallet = user_wallet_map.get(user_id)
            if user_wallet:
                user_wallet.balance = F('balance') + interest_earned_amount
                interest_earned_records.append(InterestEarned(
                    user=user['user'],
                    loan_repayment=loan_repayment,
                    interest_amount=interest_earned_amount
                ))

    # Bulk update wallets and create interest earned records
    UserWallet.objects.bulk_update(user_wallets, ['balance'])
    InterestEarned.objects.bulk_create(interest_earned_records)

def users_in_same_wallet(user):
    user_wallet = get_object_or_404(UserWallet, user=user)
    wallet = user_wallet.wallet
    user_wallets = UserWallet.objects.filter(wallet=wallet).select_related('user')
    return [{'id': uw.user.id, 'phone_number': uw.user.phone_number, "user": uw.user} for uw in user_wallets]
