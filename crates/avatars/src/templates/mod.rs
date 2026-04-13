pub mod strategist;
pub mod council;
pub mod support;

use crate::template::AvatarTemplate;

pub fn all() -> Vec<&'static AvatarTemplate> {
    let mut v: Vec<&'static AvatarTemplate> = vec![];

    v.push(strategist::template());

    v.push(council::creative::ogilvy::template());
    v.push(council::creative::bernbach::template());
    v.push(council::creative::hopkins::template());
    v.push(council::creative::draper::template());

    v.push(council::digital::patel::template());
    v.push(council::digital::vaynerchuk::template());
    v.push(council::digital::sharp::template());
    v.push(council::digital::godin::template());

    v.push(council::strategy::kotler::template());
    v.push(council::strategy::ries::template());
    v.push(council::strategy::cialdini::template());
    v.push(council::strategy::sutherland::template());

    v.push(support::qa_director::template());
    v.push(support::legal_advisor::template());
    v.push(support::analytics_director::template());
    v.push(support::brand_manager::template());
    v.push(support::market_research_lead::template());
    v.push(support::media_buyer::template());
    v.push(support::pr_director::template());
    v.push(support::growth_hacker::template());

    v
}