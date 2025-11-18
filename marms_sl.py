import streamlit as st
import random
import matplotlib.pyplot as plt
import time
import pandas as pd
import numpy as np

# --- CONFIGURATION (Constants) ---
NUM_ACCOUNTS = 10
START_EQ = 10000.0
TARGET_EQ = 11000.0
DEATH_EQ = 9000.0
MAX_TRADES = 500
LOSS_MULT_DEFAULT = 1.0 # Loss is always 1x the risked amount

# --- SIMULATION LOGIC ---

def init_accounts():
    """Initializes the list of trading accounts."""
    # Recalculate based on current parameters in session state
    risk_amount = START_EQ * st.session_state.risk_percent 

    return [{
        "id": i + 1,
        "equity": START_EQ,
        "history": [START_EQ],
        "wins": 0,
        "losses": 0,
        "total": 0,
        "status": "running" # 'running', 'finished', 'failed', 'max_trades'
    } for i in range(NUM_ACCOUNTS)]

def init_state():
    """Initializes Streamlit session state variables and default parameters."""
    if 'win_mult' not in st.session_state:
        st.session_state.win_mult = 1.5
    if 'risk_percent' not in st.session_state:
        st.session_state.risk_percent = 0.01 # 1.0%
    if 'accounts' not in st.session_state:
        st.session_state.accounts = init_accounts()
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'speed_factor' not in st.session_state:
        st.session_state.speed_factor = 1.0
    if 'all_finished' not in st.session_state:
        st.session_state.all_finished = False

def reset_sim():
    """Reresets the simulation to the initial state."""
    st.session_state.accounts = init_accounts()
    st.session_state.is_running = False
    st.session_state.all_finished = False
    st.rerun() # Trigger a full rerun to clear the UI

def simulate_trade(acc):
    """Performs a single trade simulation step for one account."""
    # Use live parameters from session state
    risk_percent = st.session_state.risk_percent
    win_mult = st.session_state.win_mult
    risk_amount = START_EQ * risk_percent
    
    # Check stop conditions
    if acc["status"] != "running" or acc["total"] >= MAX_TRADES: 
        if acc["total"] >= MAX_TRADES and acc["status"] == "running":
             acc["status"] = "max_trades" # New status for clean stop
        return

    outcome = random.choice(["win", "loss"])
    acc["total"] += 1
    
    if outcome == "win":
        acc["equity"] += risk_amount * win_mult
        acc["wins"] += 1
    else:
        acc["equity"] -= risk_amount * LOSS_MULT_DEFAULT
        acc["losses"] += 1
        
    acc["equity"] = max(0.0, acc["equity"]) # Prevent negative equity
    acc["history"].append(acc["equity"])
    
    # Check finish/fail conditions and clamp
    if acc["equity"] >= TARGET_EQ:
        acc["status"] = "finished"
        acc["equity"] = TARGET_EQ
    elif acc["equity"] <= DEATH_EQ:
        acc["status"] = "failed"
        acc["equity"] = DEATH_EQ

def run_simulation_step():
    """Runs a batch of trades and checks the global stop condition."""
    if st.session_state.is_running and not st.session_state.all_finished:
        
        # Calculate how many trades to run this step based on speed factor
        # Use a higher factor since Streamlit reruns are slow compared to Pygame clock ticks
        trades_per_step = max(1, int(st.session_state.speed_factor * 50)) 
        
        for _ in range(trades_per_step):
            if st.session_state.all_finished: break
            
            for acc in st.session_state.accounts:
                simulate_trade(acc)
            
            # Check global stop condition
            if all(a["status"] != "running" for a in st.session_state.accounts):
                st.session_state.all_finished = True
                st.session_state.is_running = False
                break

        # Re-run the script to update the UI and trigger the next step
        if st.session_state.is_running and not st.session_state.all_finished:
            # Add a slight delay for better visualization control
            time.sleep(0.01)
            st.rerun()


# --- VISUALIZATION FUNCTIONS (Matplotlib) ---

def draw_matplotlib_graph(accounts):
    """Draws the equity curves using Matplotlib."""
    # Increased figure size to utilize the full screen width
    fig, ax = plt.subplots(figsize=(16, 7)) 
    
    # 1. Determine graph scaling
    all_history = [eq for acc in accounts for eq in acc["history"]]
    
    if not all_history:
        ax.set_title("Waiting for Simulation Data...", color='gray')
        ax.set_ylim(DEATH_EQ * 0.95, TARGET_EQ * 1.05)
        return fig
        
    # Scale Y axis based on min/max of current data, ensuring target/death lines are visible
    max_y = max(TARGET_EQ * 1.05, max(all_history) * 1.05) if all_history else TARGET_EQ * 1.05
    min_y = min(DEATH_EQ * 0.95, min(all_history) * 0.95) if all_history else DEATH_EQ * 0.95
    
    # 2. Draw Key Lines
    ax.axhline(TARGET_EQ, color='limegreen', linestyle='-', linewidth=2, alpha=0.8, label=f'Target (${TARGET_EQ:,.0f})')
    ax.axhline(DEATH_EQ, color='darkred', linestyle='-', linewidth=2, alpha=0.8, label=f'Stop Out (${DEATH_EQ:,.0f})')
    ax.axhline(START_EQ, color='orange', linestyle=':', linewidth=1, alpha=0.7, label=f'Start (${START_EQ:,.0f})')
    
    # 3. Draw equity curves
    for i, acc in enumerate(accounts):
        hist = acc["history"]
        
        # Use a different color scheme to better match the Pygame green line aesthetic
        if acc["status"] == "finished":
            color = 'limegreen'
            alpha = 0.9
        elif acc["status"] == "failed":
            color = 'red'
            alpha = 0.9
        else:
            color = 'green' # Running color
            alpha = 0.7
            
        if len(hist) > 1:
            # Adding a touch of randomization to the green shades to distinguish lines
            dynamic_color = np.array(plt.cm.get_cmap('Greens')(0.5 + i / NUM_ACCOUNTS * 0.5)) * 0.8
            dynamic_color[3] = alpha # Set transparency
            
            ax.plot(hist, color=dynamic_color, linewidth=1.5, alpha=alpha)
        elif len(hist) == 1:
            ax.plot(hist, color=color, marker='o', markersize=4)

    ax.set_title("Equity Curves Over Trades", fontsize=16)
    ax.set_xlabel(f"Trade Number (Max {MAX_TRADES})", fontsize=12)
    ax.set_ylabel("Equity ($)", fontsize=12)
    ax.set_ylim(min_y, max_y)
    ax.ticklabel_format(style='plain', axis='y')
    ax.grid(True, linestyle=':', alpha=0.3)
    
    plt.tight_layout()
    return fig


# --- STREAMLIT UI LAYOUT ---

def build_metrics_panel(accounts):
    """Generates the content for the metrics panel, now split into columns below the graph."""
    
    total_trades = sum(a["total"] for a in accounts)
    total_wins = sum(a["wins"] for a in accounts)
    total_losses = sum(a["losses"] for a in accounts)
    avg_trades = total_trades / NUM_ACCOUNTS if NUM_ACCOUNTS > 0 else 0
    agg_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
    
    # Calculate live risk amount based on state
    current_risk_amount = START_EQ * st.session_state.risk_percent
    
    st.markdown("---")
    st.subheader("Simulation Metrics and Account Status")
    
    # Use columns to present the metrics panel content horizontally
    col_totals, col_accounts = st.columns([0.3, 0.7])

    with col_totals:
        # --- Portfolio Totals ---
        st.markdown("### Portfolio Totals")
        st.markdown(
            f"**R:R {LOSS_MULT_DEFAULT}:{st.session_state.win_mult}** | Risk **{st.session_state.risk_percent*100:.2f}%** "
            f"($<span style='color:red;'>{current_risk_amount:,.0f}</span>)",
            unsafe_allow_html=True
        )
        st.markdown("---")
        
        st.markdown(f"Agg Hit Rate: **<span style='color:#FFC300;'>{agg_rate:.2f}%</span>**", unsafe_allow_html=True)
        st.markdown(f"Total Trades: **{total_trades:,}**")
        st.markdown(f"Avg Trades/Acc: **{avg_trades:.1f}**")
        st.markdown(f"Total Wins: **<span style='color:green;'>{total_wins:,}</span>**", unsafe_allow_html=True)
        st.markdown(f"Total Losses: **<span style='color:red;'>{total_losses:,}</span>**", unsafe_allow_html=True)

    with col_accounts:
        st.markdown("### Individual Account Status")
        # --- Account Details (The main list) ---
        
        # Use a grid layout within the column for cleaner appearance
        cols_grid = st.columns(3)
        
        for i, acc in enumerate(accounts):
            hit_rate = (acc["wins"] / acc["total"] * 100) if acc["total"] > 0 else 0
            
            if acc["status"] == "finished":
                status_color = 'green'
                status_label = 'TARGET HIT'
            elif acc["status"] == "failed":
                status_color = 'red'
                status_label = 'DEATH HIT'
            elif acc["status"] == "max_trades":
                status_color = 'orange'
                status_label = 'MAX TRADES'
            else:
                status_color = 'blue'
                status_label = 'RUNNING'
                
            card_html = f"""
            <div style="border: 1px solid #333; padding: 10px; border-radius: 5px; margin-bottom: 10px; background-color: #1e1e1e;">
                <p style="font-weight: bold; margin: 0;">Account {acc['id']}</p>
                <p style="margin: 0; font-size: 14px;">Equity: 
                    <span style="font-weight: bold; color: {status_color};">${acc['equity']:,.0f}</span>
                </p>
                <p style="margin: 0; font-size: 12px; color: #aaa;">Status: {status_label}</p>
                <p style="margin: 0; font-size: 12px; color: #999;">Trades: {acc['total']} | W: {acc['wins']} | L: {acc['losses']} | Hit: {hit_rate:.1f}%</p>
            </div>
            """
            
            # Place account card in the correct grid column
            cols_grid[i % 3].markdown(card_html, unsafe_allow_html=True)


def build_streamlit_ui():
    """Main function to build the Streamlit user interface."""
    # Use 'wide' layout and update title
    st.set_page_config(layout="wide", page_title="MARMS Simulator")
    st.title("🛡️ Multi-Account Risk Simulation (MARMS)")
    
    init_state()

    # --- Controls Panel (Sidebar) ---
    with st.sidebar:
        st.header("Simulation Controls")
        
        # Trading Parameter Inputs
        st.subheader("Risk Parameters")
        
        # R:R Inputs (Loss Multiplier is fixed at 1.0)
        st.number_input(
            "Reward Multiplier (R in R:R)",
            min_value=1.0, 
            max_value=5.0, 
            step=0.25, 
            key='win_mult', 
            on_change=reset_sim, # Reset simulation when R:R changes
            help=f"Loss Multiplier is fixed at {LOSS_MULT_DEFAULT}x."
        )

        # Risk Percentage Input
        # Mapping for suggested percentage options (0.25%, 0.5%, 1.0%, 2.0%)
        risk_options = {
            "1.00%": 0.010,
            "0.50%": 0.005,
            "0.25%": 0.0025,
            "2.00%": 0.020
        }
        
        # Determine the initial index for the selectbox based on current state
        try:
            initial_index = list(risk_options.values()).index(st.session_state.risk_percent)
        except ValueError:
            # Handle case where current risk_percent isn't in options, default to 1.00%
            initial_index = 0 
            
        selected_risk_key = st.selectbox(
            "Risk Percentage (% of Start Equity)",
            options=list(risk_options.keys()),
            index=initial_index,
            format_func=lambda x: x,
            key='risk_percent_key',
            on_change=lambda: st.session_state.update(
                risk_percent=risk_options[st.session_state.risk_percent_key]
            )
        )
        # Force reset if risk changes
        if st.session_state.risk_percent != risk_options[selected_risk_key]:
            reset_sim()


        st.markdown("---")
        
        # Speed Control
        st.subheader("Run Speed")
        st.slider(
            "Trades Per Step Multiplier (Visual Speed)",
            min_value=0.1, max_value=5.0, step=0.1,
            value=st.session_state.speed_factor,
            key='speed_factor',
            help="Controls how many trade iterations run per Streamlit refresh."
        )

        st.markdown("---")
        
        # Start/Pause Button (Kept in sidebar for immediate access)
        if st.session_state.is_running:
            st.button("⏸️ Pause Simulation", on_click=lambda: st.session_state.update(is_running=False))
        else:
            if st.session_state.all_finished:
                st.button("🏁 Simulation Complete", disabled=True)
            else:
                st.button("▶️ Start Simulation", on_click=lambda: st.session_state.update(is_running=True))
        
        st.button("🔄 Reset Simulation", on_click=reset_sim)


    # --- Main Area: Graph on top, Metrics below ---
    
    # 1. Display Graph (Now takes up full width)
    st.pyplot(draw_matplotlib_graph(st.session_state.accounts))

    # 2. Display Metrics Panel (Now positioned below the graph)
    build_metrics_panel(st.session_state.accounts)

    # 3. Trigger the next step if running
    run_simulation_step()


if __name__ == "__main__":
    build_streamlit_ui()