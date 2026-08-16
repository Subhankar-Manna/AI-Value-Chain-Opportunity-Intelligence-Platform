import streamlit as st
import requests


API_URL = "https://ai-value-chain-opportunity-intelligence.onrender.com"



st.set_page_config(
    page_title="AI Value Chain Intelligence",
    page_icon="🤖",
    layout="wide"
)



if "selected_industry_id" not in st.session_state:
    st.session_state.selected_industry_id = None


if "selected_industry_name" not in st.session_state:
    st.session_state.selected_industry_name = None


# HELPER FUNCTIONS

def get_industries():

    response = requests.get(
        f"{API_URL}/industries"
    )

    response.raise_for_status()

    return response.json()


def build_industry(industry_name):

    response = requests.post(
        f"{API_URL}/industries/build",
        json={
            "industry": industry_name
        }
    )

    response.raise_for_status()

    return response.json()


def get_stages():

    response = requests.get(
        f"{API_URL}/stages"
    )

    response.raise_for_status()

    return response.json()


def get_processes():

    response = requests.get(
        f"{API_URL}/processes"
    )

    response.raise_for_status()

    return response.json()


def analyze_process(process_id):

    response = requests.post(
        f"{API_URL}/analyze/{process_id}"
    )

    response.raise_for_status()

    return response.json()


def get_research(process_id):

    response = requests.get(
        f"{API_URL}/research/{process_id}"
    )

    response.raise_for_status()

    return response.json()



# LOAD INDUSTRIES

try:

    industries = get_industries()

except requests.exceptions.RequestException:

    st.error(
        "Could not connect to the FastAPI backend. "
        "Please make sure the API server is running."
    )

    st.stop()


# INDUSTRY MANAGEMENT

st.markdown(
    "### 🏭 Industry Management"
)


industry_options = [
    {
        "label": industry["name"],
        "id": industry["id"],
        "name": industry["name"],
        "description": industry.get("description")
    }
    for industry in industries
]


# Add New Industry option
industry_labels = [
    industry["label"]
    for industry in industry_options
]

industry_labels.append(
    "➕ New Industry → User Input"
)


# Determine default selection

default_index = 0

if st.session_state.selected_industry_name:

    if st.session_state.selected_industry_name in industry_labels:

        default_index = industry_labels.index(
            st.session_state.selected_industry_name
        )


# INDUSTRY SELECTOR

selected_label = st.selectbox(
    "📊 Select Industry",
    industry_labels,
    index=default_index
)


# NEW INDUSTRY USER INPUT

if selected_label == "➕ New Industry → User Input":

    st.markdown("---")

    st.subheader(
        "➕ Generate New Industry"
    )

    st.write(
         "Enter an industry name and Gemini will generate "
         "a realistic end-to-end value chain."
    )

    new_industry_name = st.text_input(
        "Enter Industry Name",
        placeholder="Example: Banking"
    )


    if st.button(
        "🤖 Generate Industry with Gemini",
        type="primary"
    ):

        if not new_industry_name.strip():

            st.warning(
                "Please enter an industry name."
            )

        else:

            with st.spinner(
                f"Gemini is generating the {new_industry_name} value chain..."
            ):

                try:

                    result = build_industry(
                        new_industry_name.strip()
                    )


                    # Industry already exists

                    if result.get("message") == "Industry already exists":

                        industry_id = result.get(
                            "industry_id"
                        )

                        industry_name = result.get(
                            "industry"
                        )

                        st.session_state.selected_industry_id = (
                            industry_id
                        )

                        st.session_state.selected_industry_name = (
                            industry_name
                        )

                        st.warning(
                            f"{industry_name} already exists. "
                            "Showing the existing industry."
                        )

                        st.rerun()


                    # New industry successfully created
                    

                    industry_info = result.get(
                        "industry",
                        {}
                    )

                    industry_id = industry_info.get(
                        "id"
                    )

                    industry_name = industry_info.get(
                        "name",
                        new_industry_name.strip()
                    )


                    st.session_state.selected_industry_id = (
                        industry_id
                    )

                    st.session_state.selected_industry_name = (
                        industry_name
                    )


                    st.success(
                        f"✅ {industry_name} industry generated successfully!"
                    )

                    st.rerun()


                except requests.exceptions.RequestException as e:

                    st.error(
                        f"Industry generation failed: {e}"
                    )


    st.info(
        "💡 Example industries: Banking, "
        "Pharmaceutical, Telecommunications, "
        "Education, Insurance, Aviation."
    )

    st.stop()



# SELECT EXISTING INDUSTRY

selected_industry = next(
    (
        industry
        for industry in industry_options
        if industry["label"] == selected_label
    ),
    None
)


if selected_industry:

    st.session_state.selected_industry_id = (
        selected_industry["id"]
    )

    st.session_state.selected_industry_name = (
        selected_industry["name"]
    )


selected_industry_id = (
    st.session_state.selected_industry_id
)


selected_industry_name = (
    st.session_state.selected_industry_name
)


# LOAD STAGES AND PROCESSES

try:

    all_stages = get_stages()

    all_processes = get_processes()

except requests.exceptions.RequestException:

    st.error(
        "Could not load value-chain data."
    )

    st.stop()


# FILTER STAGES BY INDUSTRY

stages = [
    stage
    for stage in all_stages
    if stage.get("industry_id") == selected_industry_id
]

# FILTER PROCESSES BY SELECTED STAGES

stage_ids = {
    stage["id"]
    for stage in stages
}


processes = [
    process
    for process in all_processes
    if process.get("stage_id") in stage_ids
]



# HEADER

st.title(
    f"🤖 {selected_industry_name} AI Value Chain Intelligence"
)


st.caption(
    f"Identify and prioritise AI opportunities "
    f"across the {selected_industry_name.lower()} value chain."
)


st.divider()

# INDUSTRY INFORMATION

st.header(
    f"🏭 {selected_industry_name}"
)


industry_description = next(
    (
        industry["description"]
        for industry in industries
        if industry["id"] == selected_industry_id
    ),
    None
)


st.write(
    industry_description
    or f"AI-generated value chain for the "
       f"{selected_industry_name} industry."
)


st.divider()


# DASHBOARD METRICS

col1, col2, col3, col4 = st.columns(4)


# Value Chain Stages

with col1:

    st.metric(
        "Value Chain Stages",
        len(stages)
    )


# Business Processes

with col2:

    st.metric(
        "Business Processes",
        len(processes)
    )


# Analysed Opportunities

analysed = sum(
    1
    for process in processes
    if process.get("ai_opportunity")
)


with col3:

    st.metric(
        "Analysed Opportunities",
        analysed
    )



# High Priority

high_priority = sum(
    1
    for process in processes
    if process.get("priority_level") == "High"
)


with col4:

    st.metric(
        "High Priority",
        high_priority
    )


st.divider()



# VALUE CHAIN

st.header(
    f"🔗 {selected_industry_name} Value Chain"
)


if stages:

    for i, stage in enumerate(
        stages,
        start=1
    ):

        stage_processes = [
            process
            for process in processes
            if process["stage_id"] == stage["id"]
        ]


        with st.expander(
            f"{i}. {stage['name']} "
            f"({len(stage_processes)} processes)"
        ):

            st.write(
                stage["description"]
            )


            if stage_processes:

                for process in stage_processes:

                    st.markdown(
                        f"**• {process['name']}**"
                    )

            else:

                st.info(
                    "No processes available."
                )

else:

    st.warning(
        "No value-chain stages found for this industry."
    )


st.divider()


# PROCESS EXPLORER

st.header(
    "🔎 Process Explorer"
)


if processes:

    process_names = [
        process["name"]
        for process in processes
    ]


    selected_name = st.selectbox(
        "Select a process",
        process_names
    )


    selected_process = next(
        process
        for process in processes
        if process["name"] == selected_name
    )


    # SELECTED PROCESS

    st.subheader(
        selected_process["name"]
    )


    st.write(
        selected_process["description"]
        or "No description available."
    )

    # AI ANALYSIS

    st.markdown(
        "### 🤖 AI Analysis"
    )


    if st.button(
        "Analyze with AI",
        type="primary"
    ):

        with st.spinner(
            "Gemini is analysing this business process..."
        ):

            try:

                analyze_process(
                    selected_process["id"]
                )

                st.success(
                    "✅ AI analysis completed successfully!"
                )


                # Refresh processes
                all_processes = get_processes()


                processes = [
                    process
                    for process in all_processes
                    if process.get("stage_id") in stage_ids
                ]


                selected_process = next(
                    process
                    for process in processes
                    if process["id"]
                    == selected_process["id"]
                )


            except requests.exceptions.RequestException as e:

                st.error(
                    f"AI analysis failed: {e}"
                )


    st.divider()


    # BUSINESS PROBLEM / AI OPPORTUNITY

    col1, col2 = st.columns(2)


    with col1:

        st.markdown(
            "### 📌 Business Problem"
        )


        if selected_process.get(
            "business_problem"
        ):

            st.info(
                selected_process["business_problem"]
            )

        else:

            st.info(
                "AI analysis not available yet."
            )


    with col2:

        st.markdown(
            "### 💡 AI Opportunity"
        )


        if selected_process.get(
            "ai_opportunity"
        ):

            st.success(
                selected_process["ai_opportunity"]
            )

        else:

            st.info(
                "AI analysis not available yet."
            )

    # AI CAPABILITY / EXPECTED BENEFIT
    col1, col2 = st.columns(2)


    with col1:

        st.markdown(
            "### 🧠 AI Capability"
        )


        st.write(
            selected_process.get(
                "ai_capability"
            )
            or "Not analysed yet."
        )


    with col2:

        st.markdown(
            "### 📈 Expected Benefit"
        )


        st.write(
            selected_process.get(
                "expected_benefit"
            )
            or "Not analysed yet."
        )


    # RISK

    st.markdown(
        "### ⚠️ Risk"
    )


    if selected_process.get(
        "risk"
    ):

        st.warning(
            selected_process["risk"]
        )

    else:

        st.info(
            "Risk has not been analysed yet."
        )


    st.divider()


    # PRIORITY ANALYSIS

    st.markdown(
        "### ⭐ Priority Analysis"
    )


    if selected_process.get(
        "priority_score"
    ) is not None:


        col1, col2 = st.columns(2)


        with col1:

            st.metric(
                "Priority Score",
                f"{selected_process['priority_score']}/10"
            )


        with col2:

            st.metric(
                "Priority Level",
                selected_process.get(
                    "priority_level"
                )
                or "Not available"
            )


        st.markdown(
            "#### Priority Factors"
        )


        col1, col2, col3, col4 = st.columns(4)


        with col1:

            st.metric(
                "Business Value",
                selected_process.get(
                    "value_score"
                )
            )


        with col2:

            st.metric(
                "Feasibility",
                selected_process.get(
                    "feasibility_score"
                )
            )


        with col3:

            st.metric(
                "Risk",
                selected_process.get(
                    "risk_score"
                )
            )


        with col4:

            st.metric(
                "Confidence",
                selected_process.get(
                    "confidence_score"
                )
            )


    else:

        st.info(
            "Priority has not been calculated yet. "
            "Click 'Analyze with AI' to analyse this process."
        )


    st.divider()


    # RESEARCH EVIDENCE

    st.markdown(
        "### 📚 Research Evidence"
    )


    try:

        research_sources = get_research(
            selected_process["id"]
        )


        if research_sources:

            for source in research_sources:

                with st.expander(
                    source.get(
                        "title",
                        "Research Source"
                    )
                ):

                    st.markdown(
                        f"**Source Type:** "
                        f"{source.get('source_type', 'N/A')}"
                    )


                    st.markdown(
                        f"**Evidence:** "
                        f"{source.get('evidence', 'N/A')}"
                    )


                    if source.get("url"):

                        st.markdown(
                            f"**Source:** "
                            f"[View Source]"
                            f"({source['url']})"
                        )

        else:

            st.info(
                "No research evidence available "
                "for this process."
            )


    except requests.exceptions.RequestException:

        st.warning(
            "Could not load research evidence."
        )


else:

    st.info(
        "No processes available for this industry."
    )