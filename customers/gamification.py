from django.utils import timezone
from django.db.models import Sum

from .models import (
    AchievementBadge,
    CustomerAchievement,
    ImpactLevel,
    CustomerImpactMetrics,
    LeaderboardEntry,
    CommunityChallenge,
    CommunityChallengeParticipant,
)


def get_next_impact_level(points):
    """Return the highest impact level the customer qualifies for."""
    return ImpactLevel.objects.filter(min_points__lte=points).order_by('-min_points').first()


def update_impact_level(customer_metrics: CustomerImpactMetrics):
    """Update the customer's impact level based on their points."""
    level = get_next_impact_level(customer_metrics.impact_points)
    if level and customer_metrics.current_level != level:
        customer_metrics.current_level = level
        customer_metrics.save(update_fields=['current_level'])
    return level


def award_points(customer_metrics: CustomerImpactMetrics, points: int):
    """Increment impact points and update totals/level."""
    if points <= 0:
        return customer_metrics
    customer_metrics.impact_points += points
    customer_metrics.save(update_fields=['impact_points'])
    update_impact_level(customer_metrics)
    return customer_metrics


def award_badge(customer, badge: AchievementBadge):
    """Award an achievement badge to a customer if not already earned."""
    achievement, created = CustomerAchievement.objects.get_or_create(
        customer=customer,
        badge=badge,
        defaults={
            'status': 'EARNED',
            'progress': 100,
            'progress_value': badge.points_reward,
            'target_value': badge.points_reward,
            'earned_at': timezone.now(),
        }
    )
    if not created and achievement.status != 'EARNED':
        achievement.status = 'EARNED'
        achievement.progress = 100
        achievement.earned_at = timezone.now()
        achievement.save(update_fields=['status', 'progress', 'earned_at'])
    if created and badge.points_reward:
        metrics, _ = CustomerImpactMetrics.objects.get_or_create(customer=customer)
        metrics.total_badges_earned += 1
        metrics.save(update_fields=['total_badges_earned'])
        award_points(metrics, badge.points_reward)
    return achievement


def record_leaderboard_score(customer, leaderboard_type, period, score):
    """Create/update a leaderboard entry."""
    entry, _ = LeaderboardEntry.objects.get_or_create(
        customer=customer,
        leaderboard_type=leaderboard_type,
        period=period,
    )
    if score > entry.score:
        entry.score = score
        entry.save(update_fields=['score', 'last_calculated'])
    return entry


def recalc_leaderboard_ranks(leaderboard_type, period):
    """Recalculate ranks for a leaderboard."""
    entries = LeaderboardEntry.objects.filter(
        leaderboard_type=leaderboard_type,
        period=period
    ).order_by('-score', 'last_calculated')
    rank = 1
    for entry in entries:
        entry.rank = rank
        entry.save(update_fields=['rank'])
        rank += 1
    return entries


def update_challenge_progress(challenge: CommunityChallenge, customer, contribution_value: float):
    """Update a participant's progress in a community challenge."""
    participant, _ = CommunityChallengeParticipant.objects.get_or_create(
        challenge=challenge,
        customer=customer
    )
    participant.contribution_value += contribution_value
    if challenge.target_value > 0:
        participant.progress_percentage = min(
            100,
            (participant.contribution_value / challenge.target_value) * 100
        )
    if participant.progress_percentage >= 100 and not participant.completed:
        participant.completed = True
        participant.completed_at = timezone.now()
        participant.save(update_fields=['contribution_value', 'progress_percentage', 'completed', 'completed_at'])
        if challenge.reward_badge:
            award_badge(customer, challenge.reward_badge)
        if challenge.reward_points:
            metrics, _ = CustomerImpactMetrics.objects.get_or_create(customer=customer)
            award_points(metrics, challenge.reward_points)
    else:
        participant.save(update_fields=['contribution_value', 'progress_percentage'])
    return participant
