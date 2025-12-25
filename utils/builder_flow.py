import streamlit as st
from utils.ai_engine import AIEngine
from utils.resume_data import ResumeBuilder

def render_builder(builder: ResumeBuilder, ai_engine: AIEngine):
    if 'current_section' not in st.session_state:
        st.session_state.current_section = 0
    
    # Define sections sequence
    sections = [
        "Contact Information",
        "Professional Summary",
        "Technical Skills",
        "Experience",
        "Projects",
        "Education",
        "Certifications"
    ]
    
    if st.session_state.current_section >= len(sections):
        st.success("All sections completed! You can now preview and export your resume.")
        if st.button("Go to Preview"):
            st.session_state.page = 'preview'
            st.rerun()
        return

    current_section_name = sections[st.session_state.current_section]
    
    st.markdown(f"### 📝 Section {st.session_state.current_section + 1}/{len(sections)}: {current_section_name}")
    st.progress((st.session_state.current_section) / len(sections))

    # --- CHATBOT INTERFACE ---
    with st.sidebar:
        st.markdown("---")
        st.subheader(f"🤖 AI Coach ({current_section_name})")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
        # Clear chat when section changes
        if "last_section" not in st.session_state:
            st.session_state.last_section = current_section_name
        
        if st.session_state.last_section != current_section_name:
            st.session_state.chat_history = []
            st.session_state.last_section = current_section_name

        # Display history
        for msg in st.session_state.chat_history:
            st.chat_message(msg["role"]).write(msg["content"])

        # Chat input
        if prompt := st.chat_input(f"Ask about {current_section_name}..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            
            with st.spinner("Thinking..."):
                response = ai_engine.chat_with_context(current_section_name, prompt, builder.get_role())
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.chat_message("assistant").write(response)

    # --- SECTION LOGIC ---
    
    # 1. Contact Information (Form based for efficiency)
    if current_section_name == "Contact Information":
        st.info("Let's start with your contact details so recruiters can reach you.")
        with st.form("contact_form"):
            col1, col2 = st.columns(2)
            first_name = col1.text_input("First Name", placeholder="e.g. John")
            last_name = col2.text_input("Last Name", placeholder="e.g. Doe")
            phone = col1.text_input("Phone Number", placeholder="e.g. +1 123 456 7890")
            linkedin = col2.text_input("LinkedIn URL", placeholder="linkedin.com/in/johndoe")
            location = st.text_input("Location", placeholder="City, Country")
            
            submitted = st.form_submit_button("Save & Continue")
            if submitted:
                if first_name and last_name and phone:
                    data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "phone": phone,
                        "email": st.session_state.email, # Already collected
                        "linkedin": linkedin,
                        "location": location
                    }
                    builder.update_section("contact_info", data)
                    st.session_state.current_section += 1
                    st.rerun()
                else:
                    st.warning("Name and Phone are required.")

    # 2. Professional Summary (AI Assisted)
    elif current_section_name == "Professional Summary":
        st.write("Let's create a powerful summary. Tell me briefy about your years of experience and top 3 skills.")
        
        # User input for AI generation
        if 'summary_input' not in st.session_state:
            st.session_state.summary_input = ""
            
        user_input = st.text_area("Your rough input:", 
                                 placeholder="e.g. I have 2 years of experience in Python and Data Analysis. Looking for a Data Analyst role.",
                                 height=100)
        
        if st.button("Generate Professional Summary"):
            if user_input:
                with st.spinner("AI is crafting your summary..."):
                    # Extract skills from input is hard, so we just pass the text
                    generated_summary = ai_engine.generate_summary(builder.get_role(), "entry-mid level", [user_input])
                    st.session_state.generated_summary = generated_summary
            else:
                st.warning("Please provide some input.")
        
        # Display generated or existing summary
        if 'generated_summary' in st.session_state:
            st.subheader("AI Suggestion:")
            final_summary = st.text_area("Edit if needed:", st.session_state.generated_summary, height=150)
            
            if st.button("Save Summary"):
                builder.update_section("summary", final_summary)
                del st.session_state['generated_summary'] # Clean up
                st.session_state.current_section += 1
                st.rerun()

    # 3. Technical Skills (Selection + Custom)
    elif current_section_name == "Technical Skills":
        st.write(f"Add skills relevant to **{builder.get_role()}**.")
        
        # Predefined popular skills based on role (Mock list for now, ideally strictly mapped)
        common_skills = ["Python", "SQL", "Java", "React", "AWS", "Docker", "Machine Learning", "Communication"]
        
        selected_skills = st.multiselect("Select your top skills:", common_skills)
        custom_skills = st.text_input("Add other skills (comma separated):")
        
        if st.button("Save Skills"):
            final_skills = selected_skills
            if custom_skills:
                final_skills.extend([s.strip() for s in custom_skills.split(",") if s.strip()])
            
            if final_skills:
                builder.update_section("skills", final_skills)
                st.session_state.current_section += 1
                st.rerun()
            else:
                st.warning("Please add at least one skill.")

    # 4. Experience (Iterative Add)
    elif current_section_name == "Experience":
        st.write("Add your work experience or internships.")
        
        # Allow adding multiple entries
        if 'exp_entries' not in st.session_state:
            st.session_state.exp_entries = []
            
        with st.expander("Add New Position", expanded=True):
            role = st.text_input("Job Title")
            company = st.text_input("Company Name")
            duration = st.text_input("Duration (e.g. Jan 2023 - Present)")
            description = st.text_area("Key Responsibilities (rough notes):")
            
            if st.button("Optimize & Add Position"):
                if role and company:
                    with st.spinner("Optimizing bullet points..."):
                        optimized_desc = ai_engine.optimize_bullet_point(role, description or f"{role} at {company}")
                        
                        entry = {
                            "role": role,
                            "company": company,
                            "duration": duration,
                            "description": optimized_desc
                        }
                        st.session_state.exp_entries.append(entry)
                        st.success("Position added!")
                        # Clear inputs? Streamlit forms are tricky, but let's just show the list below
                else:
                    st.warning("Job Title and Company are required.")

        # Show added entries
        if st.session_state.exp_entries:
            st.write("---")
            st.subheader("Your Experience List:")
            for idx, entry in enumerate(st.session_state.exp_entries):
                st.markdown(f"**{entry['role']}** at {entry['company']}")
                st.caption(entry['duration'])
                st.markdown(entry['description'])
                st.divider()
        
        if st.button("Finish Experience Section"):
            builder.update_section("experience", st.session_state.exp_entries)
            st.session_state.current_section += 1
            st.rerun()

    # 5. Projects (Similar to Experience)
    elif current_section_name == "Projects":
        st.write("Showcase your best projects.")
        
        if 'proj_entries' not in st.session_state:
            st.session_state.proj_entries = []
            
        with st.expander("Add New Project", expanded=True):
            title = st.text_input("Project Title")
            tech = st.text_input("Tech Stack Used")
            desc = st.text_area("What did you do?")
            
            if st.button("Optimize & Add Project"):
                if title:
                    with st.spinner("Optimizing..."):
                        optimized_desc = ai_engine.optimize_bullet_point(builder.get_role(), desc or title)
                        entry = {"title": title, "tech": tech, "description": optimized_desc}
                        st.session_state.proj_entries.append(entry)
                        st.success("Project added!")
        
        if st.session_state.proj_entries:
            st.write("---")
            for p in st.session_state.proj_entries:
                st.markdown(f"**{p['title']}** ({p['tech']})")
                st.markdown(p['description'])
                st.divider()

        if st.button("Finish Projects Section"):
            builder.update_section("projects", st.session_state.proj_entries)
            st.session_state.current_section += 1
            st.rerun()

    # 6. Education
    elif current_section_name == "Education":
        st.write("Add your educational background.")
        
        with st.form("edu_form"):
            degree = st.text_input("Degree (e.g. B.Tech Computer Science)")
            school = st.text_input("University/College")
            year = st.text_input("Graduation Year")
            grade = st.text_input("CGPA / Grade (Optional)")
            
            submitted = st.form_submit_button("Save & Continue")
            if submitted:
                if degree and school:
                    data = [{
                        "degree": degree,
                        "school": school,
                        "year": year,
                        "grade": grade
                    }]
                    builder.update_section("education", data) # Simplification: only 1 education for now, or list if needed
                    st.session_state.current_section += 1
                    st.rerun()
                else:
                    st.warning("Degree and School are required.")
    
    # 7. Certifications (Optional)
    elif current_section_name == "Certifications":
        st.write("Any certifications to add?")
        
        certs = st.text_area("List Certifications (one per line):")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Skip"):
                builder.update_section("certifications", [])
                st.session_state.current_section += 1
                st.rerun()
        with col2:
            if st.button("Save Certifications"):
                cert_list = [c.strip() for c in certs.split("\n") if c.strip()]
                builder.update_section("certifications", cert_list)
                st.session_state.current_section += 1
                st.rerun()
