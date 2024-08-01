from wallet.models import UserWallet, Contribution
from shares.models import Shares
from django.db.models import Sum
from django.shortcuts import get_object_or_404


def update_user_shares(user, amount):
    # Fetch the user wallet and related data in one go
    user_wallet = get_object_or_404(UserWallet, user=user)
    wallet = user_wallet.wallet
    user_wallets = UserWallet.objects.filter(wallet=wallet).select_related('user')
    
    # Total balance of the wallet
    total_deposits_in_wallet = wallet.total_balance

    # Prepare to gather contribution totals
    user_contributions = {uw.user.id: 0 for uw in user_wallets}  # Initial dictionary to hold contributions

    # Aggregate total contributions for each user in the wallet
    contributions = Contribution.objects.filter(
        user_wallet__in=user_wallets
    ).values('user_wallet__user').annotate(total_amount=Sum('amount'))

    # Update the dictionary with actual contributions
    for contribution in contributions:
        user_id = contribution['user_wallet__user']
        user_contributions[user_id] = contribution['total_amount']
    
    # Prepare share data for bulk creation
    shares_instances = []
    for uw in user_wallets:
        user_id = uw.user.id
        total_contributions = user_contributions[user_id]
        new_share_percentage = (total_contributions / total_deposits_in_wallet * 100) if total_deposits_in_wallet else 0
        new_share_change = amount if uw.user == user else 0
        
        shares_instances.append(Shares(
            user=uw.user,
            share_change=new_share_change,
            share_percentage=new_share_percentage
        ))
    
    # Bulk create share instances
    Shares.objects.bulk_create(shares_instances)

# Assuming other functions remain the same







