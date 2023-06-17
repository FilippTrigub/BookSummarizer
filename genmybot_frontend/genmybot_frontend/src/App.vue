<template>
    <div id="App" class="container py-5">
        <div class="mb-3">
            <label class="form-label h2">{{ header }}</label>
        </div>
        <div class="mb-3">
            <label class="form-label h3">{{ description_header }}</label>
        </div>
        <div class="mb-3">
            <label class="form-label h3">Upload a file</label>
            <b-button v-b-modal.modal1 class="btn btn-info ml-2">?</b-button>
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

    <b-modal id="modal1" title="Information">
      Your custom text goes here.
    </b-modal>

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

                // Assume that `summarize` is a method of your backend server
                // And it's available at the endpoint /api/summarize
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
        cursor: pointer;
    }
    </style>
    
    <style scoped>
    #summarize-button {
        padding: 15px 30px;
    }
</style>