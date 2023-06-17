<template>
    <div id="App" class="container py-5">
        <div class="top-bar">
            <img src="logo.png" alt="Logo" class="logo" />
        </div>
        <div class="center-aligned">
            <div class="mb-3">
                <label class="form-label h2">{{ header }}</label>
            </div>
            <div class="mb-3">
                <label class="form-label h3">{{ description_header }}</label>
            </div>
            <div class="mb-3 file-upload">
                <label class="form-label h3">Upload a file</label>
                <input type="file" accept=".mp3,.wav" @change="handleFileUpload" class="form-control" />
            </div>
            <div>
                <h3 class="mb-3">Enter the first words of each part:</h3>
                <div v-for="(chapter, index) in chapters" :key="index" class="mb-3">
                    <label class="form-label">Part {{ index + 1 }}:</label>
                    <input type="text" v-model="chapters[index]" class="form-control" />
                </div>
                <button @click="addChapter" class="btn btn-primary mb-3">+</button>
            </div>
            <div class="mb-3">
                <label class="form-label h3">Email</label>
                <input type="email" v-model="email" class="form-control" />
            </div>
            <div class="mb-3">
                <label class="form-label h3">Name</label>
                <input type="text" v-model="name" class="form-control" />
            </div>
            <button id="summarize-button" @click="summarize" class="btn btn-success btn-lg">Summarize!</button>
        </div>
    </div>
</template>

<script>
    import axios from 'axios';
    import yaml from 'js-yaml';

    export default {
        data() {
            return {
                header: '',
                description_header: '',
                selectedFile: null,
                chapters: [''],
                email: '',
                name: '',
                showHelpText: false,
            };
        },
        created() {
            axios.get('config.yaml').then(response => {
                const data = yaml.load(response.data);
                this.header = data.header;
                this.description_header = data.description_header
            });
        },
        methods: {
            handleFileUpload(event) {
                this.selectedFile = event.target.files[0];
            },
            addChapter() {
                this.chapters.push('');
            },
            toggleHelpText() {
                this.showHelpText = !this.showHelpText;
            },
            summarize() {
                if (!this.selectedFile || !this.email || !this.name) {
                    alert('Please fill all fields before summarizing');
                    return;
                }

                const formData = new FormData();
                formData.append('file', this.selectedFile);
                formData.append('chapters', JSON.stringify(this.chapters));
                formData.append('email', this.email);
                formData.append('name', this.name);

                this.$http.post('/api/summarize', formData).then(response => {
                    // Handle response
                }).catch(error => {
                    // Handle error
                });
            },
        },
    };
</script>
  
<style>
    #summarize-button {
        background-color: green;
        color: white;
        padding: 15px 30px;
        font-size: 20px;
        border-radius: 5px;
        cursor: pointer}

    .top-bar {
        width: 100%;
        background-color: #f4f4f4;
        padding: 10px 0;
        position: sticky;
        top: 0;
        z-index: 9999;
    }

    .logo {
        width: 100px;
        height: auto;
        margin-left: 20px;
    }

    .center-aligned {
        display: flex;
        flex-direction: column;
        align-items: center;
        max-width: 1000px; /* Adjust to your preferred width */
        margin: auto;
    }

    .center-aligned .form-control {
        width: 100%;
    }

    .file-upload {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .mb-3 {
        margin-bottom: 30px; /* Adjust to your preferred spacing */
    }
</style>
