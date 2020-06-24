<template>
  <v-card>
    <v-card-title>
      Projects
      <v-spacer></v-spacer>
      <v-text-field
        v-model="search"
        append-icon="mdi-magnify"
        label="Search"
        single-line
        hide-details
      ></v-text-field>
      <v-spacer></v-spacer>
      <v-dialog v-model="dialog" max-width="500px">
        <!-- <template v-slot:activator="{ on }">
          <v-btn color="primary" dark class="mb-2" v-on="on">New Project</v-btn>
        </template> -->
        <v-card>
          <v-card-title>
            <span class="headline">{{ formTitle }}</span>
          </v-card-title>

          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" sm="12" md="12">
                  <v-text-field
                    v-model="editedItem.name"
                    label="Project name"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" text @click="close">Cancel</v-btn>
            <v-btn color="blue darken-1" text @click="save">Save</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-card-title>
    <v-data-table
      :headers="headers"
      :items="getProjectData"
      :search="search"
      class="elevation-1"
      :loading="isPageLoading"
      loading-text="Loading... Please wait"
    >
      <template v-slot:item.actions="{ item }">
        <!-- <v-icon small class="mr-2" @click="openProjectPage(item)"
          >mdi-open-in-new</v-icon
        > -->
        <v-btn color="primary" small @click="openProjectPage(item)">View</v-btn>
        <!-- <v-icon small class="mr-2" @click="editItem(item)">mdi-pencil</v-icon>
        <v-icon small @click="deleteItem(item)">mdi-delete</v-icon> -->
      </template>
      <template v-slot:no-data>
        <v-btn color="primary" @click="initialize">Refresh</v-btn>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  data() {
    return {
      dialog: false,
      search: '',
      loading: false,
      headers: [
        {
          text: 'Name',
          align: 'start',
          sortable: true,
          value: 'name'
        },
        { text: 'Actions', value: 'actions', sortable: false }
      ],
      editedIndex: -1,
      editedItem: {
        name: ''
      },
      defaultItem: {
        name: ''
      }
    }
  },
  computed: {
    formTitle() {
      return this.editedIndex === -1 ? 'New Project' : 'Edit Project'
    },
    ...mapGetters('projects', {
      isPageLoading: 'isPageLoading',
      getProjectData: 'getProjectData'
    })
  },
  watch: {
    dialog(val) {
      val || this.close()
    }
  },
  mounted() {
    this.initialize()
  },
  methods: {
    ...mapActions('projects', ['showPageLoading', 'fetchProjectData']),
    initialize() {
      this.showPageLoading(true)
      this.fetchProjectData()
    },
    openProjectPage(item) {
      this.$router.push('/projects/' + item.name + '/project')
    },

    editItem(item) {
      this.editedIndex = this.desserts.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialog = true
    },

    deleteItem(item) {
      this.desserts.indexOf(item)
    },

    close() {
      this.dialog = false
    },

    save() {
      if (this.editedIndex > -1) {
        Object.assign(this.desserts[this.editedIndex], this.editedItem)
      } else {
        this.desserts.push(this.editedItem)
      }
      this.close()
    }
  }
}
</script>
