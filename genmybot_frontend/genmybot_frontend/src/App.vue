<template>
    <v-app id="App">
        <v-app-bar app color="indigo" dark>
            <v-img src="logo.png" alt="Logo" class="logo" />
        </v-app-bar>
        <v-container class="py-5">
            <v-row justify="center">
                <v-col cols="12" md="8">
                    <v-subheader class="mb-3">{{ header }}</v-subheader>
                    <v-subheader class="mb-3">{{ description_header }}</v-subheader>
                    <v-file-input class="mb-3" accept=".mp3,.wav" @change="handleFileUpload" label="Upload a file"></v-file-input>
                    <v-subheader class="mb-3">Enter the first words of each part:</v-subheader>
                    <v-text-field
                        v-for="(chapter, index) in chapters"
                        :key="index"
                        class="mb-3"
                        label="Part"
                        v-model="chapters[index]"
                    ></v-text-field>
                    <v-btn @click="addChapter" class="mb-3" color="primary">+</v-btn>
                    <v-text-field class="mb-3" label="Email" v-model="email"></v-text-field>
                    <v-text-field class="mb-3" label="Name" v-model="name"></v-text-field>
                    <v-btn @click="summarize" class="btn btn-success btn-lg" color="green">Summarize!</v-btn>
                </v-col>
            </v-row>
        </v-container>
    </v-app>
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

<style scoped>
    .v-subheader {
        margin-bottom: 15px;
    }
</style>
