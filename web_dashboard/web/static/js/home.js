var report_selections = new Array();

var ReportUserBlock = React.createClass({displayName: 'ReportUserBlock',
    render: function() {
        var i = 0;
        var commitLines = this.props.block.PullRequests.map(function(pr){
            i++;
            return(<div key={i} className="user-report-line">{pr.title} -- <a target="_blank" href={pr.url}>{pr.url}</a></div>);
        });
        return(
            <div className="user-report-block">
                <div>{this.props.block.Author}</div>
                {commitLines}
            </div>
        );
    }
});

var ReportRepositoryBlock = React.createClass({displayName: 'ReportRepositoryBlock',
    render: function () {
        var userBlocks = this.props.repo.CommitGroups.map(function(group){
            var key = group.Author;
            return (<ReportUserBlock key={key} block={group} />)
        });
        return(
            <div className="report-repo-block">
                <div>Repository: {this.props.repo.Owner}/{this.props.repo.Name}</div>
                <div>From: {this.props.repo.FromTag}</div>
                <div>To: {this.props.repo.ToTag}</div>
                {userBlocks}
            </div>
        );
    }
});

var ReportDisplay = React.createClass({"displayName": "ReportDisplay",
    render: function(){
        var repoBlocks = this.props.report.Repos.map(function(repo){
            var key = repo.Owner + "/" + repo.Name;
            return (<ReportRepositoryBlock key={key} repo={repo} />)
        });
        return(
            <div className="report-block" data-desc="main container for the report output">
                <div>Generated: {this.props.report.GeneratedAt}</div>
                {repoBlocks}
            </div>
        );
    }
});

var TagSelector = React.createClass({displayName: 'TagSelector',
    loadData: function(){
        $.ajax('/get_tags/' + this.props.repo.Owner + '/' + this.props.repo.Name, {
            dataType: 'json',
            success: function(data, textStatus, jqXHR){
                this.setState({tags: data});
            }.bind(this),
            error: function(jqXHR, textStatus, errorThrown){
                release_util.logging.error('DEBUGGING; Ajax query to get repos failed.');
            }.bind(this)
        });
    },
    componentDidMount: function(){
        this.loadData();
    },
    getInitialState: function(){
        return {tags: [],
                toTag: "HEAD"};
    },
    onFromChanged: function(e){
        var key = this.props.repo.Owner + '/' + this.props.repo.Name;
        report_selections[key] = {
            Owner: this.props.repo.Owner,
            Name: this.props.repo.Name,
            tags: this.state.tags,
            fromTag: $(e.currentTarget).val(),
            toTag: this.state.toTag
        };
        this.setState({
            Owner: this.props.repo.Owner,
            Name: this.props.repo.Name,
            tags: this.state.tags,
            fromTag: $(e.currentTarget).val(),
            toTag: this.state.toTag
        });
    },
    onToChanged: function(e){
        var key = this.props.repo.Owner + '/' + this.props.repo.Name;
        report_selections[key] = {
            Owner: this.props.repo.Owner,
            Name: this.props.repo.Name,
            tags: this.state.tags,
            fromTag: this.state.toTag,
            toTag: $(e.currentTarget).val()
        };
        this.setState({
            tags: this.state.tags,
            fromTag: this.state.fromTag,
            toTag: $(e.currentTarget).val()
        });
    },
    render: function(){
        if (this.state.tags.length < 1) {
            return (<div>loading...</div>)
        }

        var tags = this.state.tags.map(function(tag){
            return (<option key={tag} value={tag}>{tag}</option>)
        });

        return(
            <div className="tag-selector">
                <div>
                    From:
                    <select onChange={this.onFromChanged} defaultValue="">
                        <option> </option>
                        <option value="HEAD">HEAD</option>
                        {tags}
                    </select>
                </div>
                <div>
                    To:
                    <select onChange={this.onToChanged} defaultValue="HEAD">
                        <option> </option>
                        <option value="HEAD">HEAD</option>
                        {tags}
                    </select>
                </div>
            </div>
        );
    }
});

var RepositoriesItem = React.createClass({displayName: 'RepositoriesItem',
    handleItemChecked: function(e){
        var element = $(e.currentTarget);
        var owner = this.props.repo.Owner;
        var name = this.props.repo.Name;
        var data = owner + '/' + name;
        if (element.is(':checked')){
            this.setState({repoChecked: true});
            release_util.logging.debug(data + " checked.");
        }else{
            this.setState({repoChecked: false});
            delete report_selections[data];
            release_util.logging.debug(data + " unchecked.");
        }
    },
    getInitialState: function(){
        return {repoChecked: false };
    },
    render: function(){
        return (
            <div className="RepositoriesItem">
                <input type="checkbox"
                       onClick={this.handleItemChecked}
                />
                {this.props.repo.Owner}/{this.props.repo.Name}
                {this.state.repoChecked ? <TagSelector repo={this.props.repo} /> : null}
            </div>
        );
    }
});

var RepositoryList = React.createClass({displayName: 'RepositoryList',
    loadData: function() {
        $.ajax('/list_repos/', {
            dataType: 'json',
            success: function(data, textStatus, jqXHR){
                this.setState({data: data});
            }.bind(this),
            error: function(jqXHR, textStatus, errorThrown){
                release_util.logging.error('DEBUGGING; Ajax query to get repos failed.');
            }.bind(this)
        });
    },
    handleGenerateReportClick: function() {
        var keys = Object.keys(report_selections);
        var input = [];
        var repoListThis = this;

        // debugger;
        this.setState({data: repoListThis.state.data});

        for (var i = 0; i < keys.length; i++) {
            var o = report_selections[keys[i]];
            input.push({
                Owner: o.Owner,
                Name: o.Name,
                FromTag: o.fromTag,
                ToTag: o.toTag
            });
        }

        if (keys.length > 0) {
            $.ajax('/generate_report/', {
                type: "POST",
                contentType: 'application/json',
                data: JSON.stringify(input),
                dataType: 'text',
                success: function (data, textStatus, jqXHR) {
                    // debugger;
                    repoListThis.setState({
                        data: repoListThis.state.data,
                        report: JSON.parse(data)
                    });
                }
            });
        }
    },
    handleExportReport: function(){
        $.fileDownload('/export_report/?ExportId=' + this.state.report.ExportId);
    },
    componentDidMount: function() {
        this.loadData();
    },
    getInitialState: function() {
        return {data: []};
    },
    render: function() {
        var items = this.state.data.map(function(repo){
            var key = repo.Owner + "/" + repo.Name;
            return (<RepositoriesItem key={key} repo={repo} />)
        });
        return(
            <div>
                {items}
                <input type="button" className="btn btn-primary" onClick={this.handleGenerateReportClick} value="Generate Report" />
                {this.state.report != null && this.state.report.ExportId != null ? <input type="button" className="btn" onClick={this.handleExportReport} value="Download Report" /> : null}
                {this.state.report != null ? <ReportDisplay report={this.state.report} /> : null}
            </div>
        );
    }
});

ReactDOM.render(
    <RepositoryList />,
    document.getElementById('repoList')
);
