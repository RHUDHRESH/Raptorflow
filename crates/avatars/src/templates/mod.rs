pub mod council;
pub mod strategist;
pub mod support;

use crate::template::AvatarTemplate;

pub fn all() -> Vec<&'static AvatarTemplate> {
    vec![
        strategist::template(),
        council::creative::ogilvy::template(),
        council::creative::bernbach::template(),
        council::creative::hopkins::template(),
        council::creative::draper::template(),
        council::digital::patel::template(),
        council::digital::vaynerchuk::template(),
        council::digital::sharp::template(),
        council::digital::godin::template(),
        council::strategy::kotler::template(),
        council::strategy::ries::template(),
        council::strategy::cialdini::template(),
        council::strategy::sutherland::template(),
        support::qa_director::template(),
        support::legal_advisor::template(),
        support::analytics_director::template(),
        support::brand_manager::template(),
        support::market_research_lead::template(),
        support::media_buyer::template(),
        support::pr_director::template(),
        support::growth_hacker::template(),
    ]
}
