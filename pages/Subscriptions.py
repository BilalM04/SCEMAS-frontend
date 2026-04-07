import streamlit as st

from clients.AlertClient import (
    get_all_alert_rules,
    get_my_subscriptions,
    subscribe_to_alert,
    unsubscribe_from_alert,
)
from models.SensorType import SensorType
from utils.Initialize import initialize
from utils.Sidebar import render_sidebar

# -----------------------
# Page Setup
# -----------------------
st.set_page_config(layout="wide")
st.session_state.page = "subscriptions"

initialize()
render_sidebar()

st.title('📧 Subscriptions')
st.caption('Manage your alert subscriptions. Subscribe to rules to receive notifications when thresholds are breached.')

# -----------------------
# Dialog Functions
# -----------------------
@st.dialog("Confirm Subscription")
def confirm_subscribe_dialog(rule_id, rule_name):
    st.write(f"Are you sure you want to subscribe to **{rule_name}**?")

    if st.button("Confirm", use_container_width=True):
        try:
            subscribe_to_alert(rule_id)
            st.session_state.toast = {
                "message": f"Subscribed to {rule_name}.",
                "icon": ":material/check:"
            }
            st.session_state.refresh_subscriptions = True
        except Exception:
            st.session_state.toast = {
                "message": f"Failed to subscribe.",
                "icon": ":material/error:"
            }
        st.rerun()


@st.dialog("Confirm Unsubscribe")
def confirm_unsubscribe_dialog(rule_id, rule_name):
    st.write(f"Are you sure you want to unsubscribe from **{rule_name}**?")

    if st.button("Confirm", use_container_width=True):
        try:
            unsubscribe_from_alert(rule_id)
            st.session_state.toast = {
                "message": f"Unsubscribed from {rule_name}.",
                "icon": ":material/check:"
            }
            st.session_state.refresh_subscriptions = True
        except Exception:
            st.session_state.toast = {
                "message": f"Failed to unsubscribe.",
                "icon": ":material/error:"
            }
        st.rerun()

# -----------------------
# Load Data
# -----------------------
if st.session_state.my_subscriptions is None or st.session_state.refresh_subscriptions == True:
    try:
        st.session_state.refresh_subscriptions = False
        st.session_state.my_subscriptions = get_my_subscriptions()
    except Exception:
        st.error("Failed to fetch your subscriptions.")
        st.stop()

if st.session_state.subscriptions_alert_rules is None:
    try:
        st.session_state.subscriptions_alert_rules = get_all_alert_rules()
    except Exception:
        st.error("Failed to fetch alert rules.")
        st.stop()

my_subscriptions = st.session_state.my_subscriptions
subscribed_rule_ids = {s.rule_id for s in my_subscriptions}

all_rules = st.session_state.subscriptions_alert_rules

# -----------------------
# Tabs
# -----------------------
my_subscriptions_tab, alert_rules_tab = st.tabs(["📋 My Subscriptions", "🔔 Available Alert Rules"])

# -----------------------
# My Subscriptions
# -----------------------
with my_subscriptions_tab:
    st.subheader("My Subscriptions")

    if not my_subscriptions:
        st.info("You are not subscribed to any alert rules yet.")
    else:
        for sub in my_subscriptions:
            col1, col2 = st.columns([5, 1])

            with col1:
                st.markdown(f"**{sub.rule_name}**")
                st.caption(f"Rule ID: `{sub.rule_id}` · Subscription ID: `{sub.subscription_id}`")

            with col2:
                if st.button("Unsubscribe", key=f"unsub_{sub.subscription_id}", use_container_width=True):
                    confirm_unsubscribe_dialog(sub.rule_id, sub.rule_name)

# -----------------------
# Available Rules
# -----------------------
with alert_rules_tab:
    st.subheader("Available Alert Rules")
    st.caption("Browse all active alert rules and subscribe to ones relevant to you.")

    if not all_rules:
        st.info("No alert rules are currently available.")
    else:
        # -----------------------
        # Filter
        # -----------------------
        filter_cols = st.columns(2)

        sensor_filter = filter_cols[0].selectbox(
            "Filter by Sensor Type",
            options=[None] + list(SensorType),
            format_func=lambda x: x.value if x else "All"
        )

        search = filter_cols[1].text_input("Search by Rule Name")

        filtered_rules = all_rules

        if sensor_filter:
            filtered_rules = [r for r in filtered_rules if r.sensor_type == sensor_filter]

        if search:
            filtered_rules = [r for r in filtered_rules if search.lower() in r.name.lower()]

        if not filtered_rules:
            st.warning("No rules match the selected filters.")
        else:
            for rule in filtered_rules:
                is_subscribed = rule.rule_id in subscribed_rule_ids

                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 2, 1])

                    with col1:
                        st.markdown(f"**{rule.name}**")
                        st.caption(
                            f"📡 {rule.sensor_type.value.title()} · "
                            f"Threshold: `{rule.threshold}` · "
                            f"Operator: `{rule.operator.value}`"
                        )

                    with col2:
                        st.caption(
                            f"📍 Lat: `{rule.location.latitude:.4f}`, "
                            f"Lon: `{rule.location.longitude:.4f}` · "
                            f"Radius: `{rule.radius} km`"
                        )

                    with col3:
                        if is_subscribed:
                            st.success("Subscribed")
                            if st.button("Unsubscribe", key=f"unsub_rule_{rule.rule_id}", use_container_width=True):
                                confirm_unsubscribe_dialog(rule.rule_id, rule.name)
                        else:
                            if st.button("Subscribe", key=f"sub_rule_{rule.rule_id}", use_container_width=True):
                                confirm_subscribe_dialog(rule.rule_id, rule.name)