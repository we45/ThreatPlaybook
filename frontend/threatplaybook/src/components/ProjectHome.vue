<template>
    <div>
        <nav-bar></nav-bar>
        <br>
        <b-container fluid>
            <h3>Projects</h3>
            <hr>
            <br>
            <b-row>
                <b-col md="6" class="my-1">
                    <b-form-group label-cols-sm="3" label="Filter" class="mb-0">
                        <b-input-group>
                            <b-form-input v-model="filter" placeholder="Type to Search"/>
                            <b-input-group-append>
                                <b-button :disabled="!filter" @click="filter = ''">Clear</b-button>
                            </b-input-group-append>
                        </b-input-group>
                    </b-form-group>
                </b-col>
                <b-col md="6" class="my-1">
                    <b-form-group label-cols-sm="3" label="Per page" class="mb-0">
                        <b-form-select :options="pageOptions" v-model="perPage"/>
                    </b-form-group>
                </b-col>
            </b-row>
            <b-row>
                <br>
                <b-col md="6" class="my-1">
                </b-col>
                <br>
                <br>
                <b-col md="6" class="my-1">
                    <br>
                    <b-pagination
                            :total-rows="totalRows"
                            :per-page="perPage"
                            v-model="currentPage"
                            style="float: right;"/>
                </b-col>
            </b-row>
            <b-row>
                <b-table
                        striped hover
                        show-empty
                        stacked="md"
                        :items="projectQuery"
                        :fields="fields"
                        :current-page="currentPage"
                        :per-page="perPage"
                        :filter="filter"
                >
                    <template slot="name" slot-scope="row">
                        <a @click="goToProject(row.value)" style="cursor: pointer;">
                            {{ row.value }}
                        </a>
                    </template>

                    <template slot="actions" slot-scope="row">
                        <b-button size="sm" @click="goToProjectMap(row.item.name)" class="btn-purple" style="margin-right: 4px;">
                            Threat Map
                        </b-button>
                        <b-button size="sm" @click="goToUserStoryMap(row.item.name)" class="btn-purple">
                            User Story Map
                        </b-button>
                    </template>

                </b-table>
            </b-row>
        </b-container>
    </div>
</template>
<script>
    import Navbar from "./Navbar.vue";
    import gql from "graphql-tag";

    const items = []
    export default {
        components: {
            "nav-bar": Navbar
        },
        data() {
            return {
                items: items,
                fields: [
                    {key: 'name', label: 'Project Name'},
                    {key: 'actions', label: 'Actions', class: 'text-right'}
                ],
                currentPage: 1,
                perPage: 5,
                totalRows: items.length,
                pageOptions: [5, 10, 15, 25, 50],
                filter: null
            };
        },
        apollo: {
            projectQuery: {
                query: gql`
        query {
          projects {
            id
            name
          }
        }
      `,
                update: result => result.projects
            }
        },
        methods: {
            goToProject(item_name) {
                this.$router.push("/project/" + btoa(item_name));
            },
            goToProjectMap(item_name) {
                this.$router.push("/map/" + btoa(item_name));
            },
            goToUserStoryMap(item_name) {
                this.$router.push("/story/" + btoa(item_name));
            }
        }
    };
</script>

<style scoped>
    .btn-purple {
        color: #f9f2f4;
        background-color: #1C1D21;
        border-color: #1C1D21;
        border-radius: 14px;
        padding: 3px 12px;
        margin-bottom: 0;
        font-size: 14px;
    }

    .btn-purple:focus,
    .btn-purple.focus {
        color: #1C1D21;
        background-color: #f9f2f4;
        border-color: #1C1D21;
        border-radius: 14px;
        padding: 3px 12px;
        margin-bottom: 0;
        font-size: 14px;
    }

    .btn-purple:hover {
        color: #1C1D21;
        background-color: #f9f2f4;
        border-color: #1C1D21;
        border-radius: 14px;
        padding: 3px 12px;
        margin-bottom: 0;
        font-size: 14px;
    }
</style>
