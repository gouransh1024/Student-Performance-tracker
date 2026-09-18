"""
Interactive Chart Theme & Data Visualization Utilities
Built with Plotly for responsive academic analytics with dynamic Light/Dark mode support
"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Curated modern color tokens
BRAND_INDIGO = "#6366F1"
BRAND_VIOLET = "#8B5CF6"
BRAND_CYAN = "#06B6D4"
BRAND_EMERALD = "#10B981"
BRAND_AMBER = "#F59E0B"
BRAND_ROSE = "#EF4444"

GRADE_COLOR_MAP = {
    'A+': '#10B981',  # Emerald
    'A': '#06B6D4',   # Cyan
    'B+': '#3B82F6',  # Blue
    'B': '#6366F1',   # Indigo
    'C+': '#F59E0B',  # Amber
    'C': '#F97316',   # Orange
    'F': '#EF4444'    # Rose / Red
}

def _is_dark_mode() -> bool:
    """Check if dark mode is active in session state"""
    try:
        return st.session_state.get('app_theme', 'dark') == "dark"
    except Exception:
        return True

def apply_chart_style(fig: go.Figure, title: str = None, height: int = 420) -> go.Figure:
    """Applies modern typography, dynamic light/dark contrast, and transparent background to Plotly figures"""
    is_dark = _is_dark_mode()
    title_color = "#F8FAFC" if is_dark else "#0F172A"
    font_color = "#CBD5E1" if is_dark else "#475569"
    grid_color = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(226, 232, 240, 0.7)"
    hover_bg = "#1E293B" if is_dark else "#0F172A"
    hover_text = "#F8FAFC" if is_dark else "#FFFFFF"

    fig.update_layout(
        title={
            'text': title if title else '',
            'font': {'family': 'Plus Jakarta Sans, Inter, sans-serif', 'size': 16, 'color': title_color},
            'x': 0.02,
            'xanchor': 'left'
        } if title else None,
        font={'family': 'Inter, sans-serif', 'color': font_color},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=30, r=30, t=50 if title else 20, b=30),
        height=height,
        hoverlabel=dict(
            bgcolor=hover_bg,
            font_size=12,
            font_family="Inter, sans-serif",
            font_color=hover_text
        ),
        legend=dict(
            font=dict(color=font_color, family="Inter")
        )
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor=grid_color,
        zeroline=False,
        color=font_color
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=grid_color,
        zeroline=False,
        color=font_color
    )
    return fig

def create_subject_radar_chart(subject_details: list) -> go.Figure:
    """
    Generate an aesthetic spider/radar chart displaying competencies across all subjects.
    
    Args:
        subject_details: List of dicts with 'subject' and 'percentage' keys
    """
    is_dark = _is_dark_mode()
    font_color = "#CBD5E1" if is_dark else "#475569"
    polar_bg = "rgba(30, 41, 59, 0.45)" if is_dark else "rgba(248, 250, 252, 0.6)"
    polar_grid = "rgba(255, 255, 255, 0.12)" if is_dark else "rgba(226, 232, 240, 0.8)"
    polar_line = "rgba(255, 255, 255, 0.2)" if is_dark else "rgba(203, 213, 225, 0.9)"

    if not subject_details:
        fig = go.Figure()
        fig.add_annotation(text="No subject data recorded", showarrow=False, font=dict(size=14, color="#94A3B8"))
        return apply_chart_style(fig, "Subject Competency Profile", height=380)

    categories = [d.get('subject', f"Subj {i+1}") for i, d in enumerate(subject_details)]
    percentages = [float(d.get('percentage', 0.0)) for d in subject_details]

    # Close the radar loop
    categories_closed = categories + [categories[0]]
    percentages_closed = percentages + [percentages[0]]

    fig = go.Figure()

    # Benchmark polygon (Target: 75% proficient)
    fig.add_trace(go.Scatterpolar(
        r=[75] * len(categories_closed),
        theta=categories_closed,
        fill=None,
        mode='lines',
        name='Benchmark (75%)',
        line=dict(color='rgba(165, 180, 252, 0.6)' if is_dark else 'rgba(148, 163, 184, 0.7)', width=1.5, dash='dash')
    ))

    # Student polygon
    fig.add_trace(go.Scatterpolar(
        r=percentages_closed,
        theta=categories_closed,
        fill='toself',
        name='Student Mastery',
        fillcolor='rgba(99, 102, 241, 0.35)',
        line=dict(color=BRAND_INDIGO, width=2.5),
        marker=dict(size=6, color=BRAND_VIOLET)
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[20, 40, 60, 80, 100],
                ticktext=['20%', '40%', '60%', '80%', '100%'],
                gridcolor=polar_grid,
                linecolor=polar_line,
                tickfont=dict(color=font_color, size=10)
            ),
            angularaxis=dict(
                gridcolor=polar_grid,
                linecolor=polar_line,
                tickfont=dict(color=font_color, size=11, family="Inter")
            ),
            bgcolor=polar_bg
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(color=font_color))
    )

    return apply_chart_style(fig, "Subject Mastery Balance (Radar Profile)", height=420)

def create_class_heatmap(matrix_df: pd.DataFrame, title: str = "Class Subject Mastery Matrix (%)") -> go.Figure:
    """
    Generate an interactive heatmap of Students (rows) vs Subjects (columns) with percentage scores.
    """
    if matrix_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No class matrix data available", showarrow=False, font=dict(size=14, color="#94A3B8"))
        return apply_chart_style(fig, title, height=400)

    z_values = matrix_df.values
    x_labels = list(matrix_df.columns)
    y_labels = list(matrix_df.index)

    text_annotations = []
    for row in z_values:
        row_text = []
        for val in row:
            if pd.isna(val) or val == 0:
                row_text.append("-")
            else:
                row_text.append(f"{val:.0f}%")
        text_annotations.append(row_text)

    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=x_labels,
        y=y_labels,
        text=text_annotations,
        texttemplate="%{text}",
        textfont={"family": "Inter, sans-serif", "size": 11, "color": "#FFFFFF"},
        colorscale=[
            [0.0, '#EF4444'],   # <40 Fail (Red)
            [0.4, '#F59E0B'],   # 40-60 Average (Amber)
            [0.7, '#3B82F6'],   # 60-80 Good (Blue)
            [1.0, '#10B981']    # 80-100 Excellent (Emerald)
        ],
        zmin=0,
        zmax=100,
        colorbar=dict(
            title=dict(text="Score %", font=dict(family="Inter", size=12)),
            thickness=14,
            len=0.8
        ),
        hoverongaps=False
    ))

    fig.update_layout(
        xaxis=dict(tickangle=-25, side='bottom'),
        yaxis=dict(autorange="reversed")
    )

    calc_height = max(380, len(y_labels) * 35 + 120)
    return apply_chart_style(fig, title, height=min(calc_height, 700))

def create_attendance_scatter(correlation_data: list) -> go.Figure:
    """
    Scatter plot of Attendance % (x-axis) vs Average Score % (y-axis) with OLS trendline.
    
    Args:
        correlation_data: List of dicts with 'student_name', 'attendance_pct', 'academic_avg', 'status'
    """
    if not correlation_data:
        fig = go.Figure()
        fig.add_annotation(text="No correlation data available", showarrow=False, font=dict(size=14, color="#94A3B8"))
        return apply_chart_style(fig, "Attendance vs. Academic Performance Correlation", height=420)

    df = pd.DataFrame(correlation_data)
    df = df[df['attendance_pct'].notna() & df['academic_avg'].notna()]
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Insufficient data points for correlation", showarrow=False, font=dict(size=14, color="#94A3B8"))
        return apply_chart_style(fig, "Attendance vs. Academic Performance Correlation", height=420)

    x = df['attendance_pct'].values
    y = df['academic_avg'].values

    color_discrete_map = {
        'Pass': BRAND_EMERALD,
        'Fail': BRAND_ROSE
    }
    point_colors = [color_discrete_map.get(s, BRAND_INDIGO) for s in df['status']]

    fig = go.Figure()

    is_dark = _is_dark_mode()
    label_color = "#CBD5E1" if is_dark else "#64748B"

    # Points
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='markers+text',
        name='Students',
        text=[name.split()[0] for name in df['student_name']],
        textposition='top center',
        textfont=dict(size=9, family="Inter", color=label_color),
        marker=dict(
            size=11,
            color=point_colors,
            line=dict(width=1.5, color='#FFFFFF'),
            opacity=0.88
        ),
        hovertemplate="<b>%{customdata[0]}</b><br>" +
                      "Attendance: %{x:.1f}%<br>" +
                      "Academic Avg: %{y:.1f}%<br>" +
                      "Status: %{customdata[1]}<extra></extra>",
        customdata=df[['student_name', 'status']].values
    ))

    # Trendline
    if len(x) >= 2:
        try:
            poly_fit = np.polyfit(x, y, 1)
            poly1d_fn = np.poly1d(poly_fit)
            x_line = np.linspace(min(x), max(x), 50)
            y_line = poly1d_fn(x_line)

            corr = np.corrcoef(x, y)[0, 1]
            corr_label = f"Trendline (r = {corr:.2f})"

            fig.add_trace(go.Scatter(
                x=x_line,
                y=y_line,
                mode='lines',
                name=corr_label,
                line=dict(color=BRAND_INDIGO, width=2, dash='dash')
            ))
        except Exception:
            pass

    # Threshold markers
    fig.add_vline(x=75, line_width=1, line_dash="dot", line_color="rgba(239, 68, 68, 0.6)")
    fig.add_hline(y=40, line_width=1, line_dash="dot", line_color="rgba(239, 68, 68, 0.6)")

    fig.update_xaxes(title="Attendance Rate (%)", range=[min(40, min(x) - 5), 105])
    fig.update_yaxes(title="Overall Academic Score (%)", range=[0, 105])
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return apply_chart_style(fig, "Attendance vs. Academic Performance Correlation", height=450)

def create_grade_donut_chart(grade_counts: dict) -> go.Figure:
    """
    Generate an elegant donut chart showing grade distribution across the cohort.
    
    Args:
        grade_counts: Dict mapping grade labels ('A+', 'A', etc.) to count of students
    """
    is_dark = _is_dark_mode()
    title_center_color = "#F8FAFC" if is_dark else "#0F172A"

    if not grade_counts or sum(grade_counts.values()) == 0:
        fig = go.Figure()
        fig.add_annotation(text="No grade records found", showarrow=False, font=dict(size=14, color="#94A3B8"))
        return apply_chart_style(fig, "Grade Distribution", height=350)

    labels = list(grade_counts.keys())
    values = list(grade_counts.values())
    colors = [GRADE_COLOR_MAP.get(g, '#94A3B8') for g in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.58,
        marker=dict(colors=colors, line=dict(color='#111827' if is_dark else '#FFFFFF', width=2)),
        textinfo='label+percent',
        hoverinfo='label+value+percent',
        textfont=dict(family="Inter", size=11, color="#FFFFFF")
    )])

    total_students = sum(values)
    fig.add_annotation(
        text=f"<b>{total_students}</b><br><span style='font-size:11px;color:#94A3B8'>Students</span>",
        x=0.5, y=0.5,
        font=dict(family="Plus Jakarta Sans", size=18, color=title_center_color),
        showarrow=False
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )

    return apply_chart_style(fig, "Grade Distribution Cohort Overview", height=380)

def create_podium_bar_chart(top_students_df: pd.DataFrame) -> go.Figure:
    """
    Creates a ranked horizontal leaderboard bar chart for top performers.
    """
    if top_students_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No top performer data available", showarrow=False, font=dict(size=14, color="#94A3B8"))
        return apply_chart_style(fig, "Top Performers Leaderboard", height=380)

    df_sorted = top_students_df.sort_values(by='overall_percentage', ascending=True).tail(10)

    colors = []
    for pct in df_sorted['overall_percentage']:
        if pct >= 85:
            colors.append(BRAND_EMERALD)
        elif pct >= 70:
            colors.append(BRAND_CYAN)
        elif pct >= 50:
            colors.append(BRAND_INDIGO)
        else:
            colors.append(BRAND_AMBER)

    fig = go.Figure(go.Bar(
        x=df_sorted['overall_percentage'],
        y=df_sorted['student_name'],
        orientation='h',
        marker=dict(color=colors, line=dict(color='rgba(255,255,255,0.7)', width=1)),
        text=[f"{p:.1f}% ({g})" for p, g in zip(df_sorted['overall_percentage'], df_sorted['overall_grade'])],
        textposition='inside',
        textfont=dict(family="Inter", size=11, color="#FFFFFF"),
        hoverinfo='x+y'
    ))

    fig.update_xaxes(range=[0, 105], title="Overall Percentage (%)")
    fig.update_yaxes(title="")

    return apply_chart_style(fig, "Academic Leaderboard (Top 10)", height=max(360, len(df_sorted)*32 + 80))
