const dateFormat = 'DD.MM.YYYY',
      dayWidth = 25,
      eventHeight = 65,
      tagSep = 'a',
      monthNames = [
        'Январь',
        'Февраль',
        'Март',
        'Апрель',
        'Май',
        'Июнь',
        'Июль',
        'Август',
        'Сентябрь',
        'Октябрь',
        'Ноябрь',
        'Декабрь',
    ],
    monthDeclensions = [
        'января',
        'февраля',
        'марта',
        'апреля',
        'мая',
        'июня',
        'июля',
        'августа',
        'сентября',
        'октября',
        'ноября',
        'декабря',
    ]
;

function renderTripper(weekendList, noWeekendList, eventSource, tagGroups){
    // Calendar first month
    const today = moment().startOf('day'),
          eventList = getEvents(eventSource)
    ;

    const app = new Vue({
        el: '#app',
        data: {
            width: 0,
            height: 0,
            tags: tagGroups,
            applyTags: Array.from({length: tagGroups.length}, () => []),
            applySearch: '',
            filterCounter: 0,
            months: [],
            filteredEvents: eventList,
            stripes: [],
            eventCounter: 0,
            detail: {
                show: false,
                event: null,
                prev: null,
                next: null,
            },
            menu: {
                mobile: false,
            }
        },
        filters: {
            pluralize: function(value, one, two, three){
                const cases = [2, 0, 1, 1, 1, 2],
                     titles = [one, two, three],
                        key = (value % 100 > 4 && value % 100 < 20) ? 2 : cases[(value % 10 < 5) ? value % 10 : 5]
                ;
                return titles[key];
            }
        },
        created: function() {
            const self = this,
                  urlParams = new URLSearchParams(window.location.search),
                  tags = atob(urlParams.get('t') || '').split(tagSep).map((t) => parseInt(t) || 0),
                  search = urlParams.get('q')
              ;

            for (let i = 0; i < tags.length; i++){
                this.tags[i].tags.map(function(t){
                    if (t.bit & tags[i]) {
                        self.applyTags[i].push(t.bit);
                    }
                });
            }

            if (search){
                this.applySearch = search.trim();
            }

            // Closes event detail on ESC
            document.addEventListener('keyup', function (evt) {
                if (evt.keyCode === 27) {
                    self.hideDetail();
                }
            });
        },
        mounted: function() {
            let showEvent = window.location.hash.substr(1);
            if (showEvent){
                this.showDetail(showEvent);
            } else if (!this.filterCounter) {
                this.showMenu();
            }
        },
        computed: {
            eventFilter(){
                let self = this,
                    events = eventList,
                    newParams = [],
                    query = this.applySearch.trim().toLowerCase(),
                    applyTags = this.applyTags.map(function(g){
                        return g.reduce((a, b) => a | b, 0);
                    })
                ;

                if (query){
                    newParams.push('q=' + query);
                }

                if (applyTags.some((x) => x)){
                    newParams.push(tagsToParams(applyTags))
                }

                updateUrl(
                    newParams.join('&'),
                    null,
                );

                if (query){
                    events = events.filter((e) => e.norm.indexOf(query) != -1);
                }

                for (let i = 0; i < this.tags.length; i++){
                    let group = this.tags[i];

                    // Collects possible events
                    let groupEvents = events;
                    for (let j = 0; j < self.tags.length; j++){
                        let bits = applyTags[j];
                        if (i != j && bits) {
                            groupEvents = groupEvents.filter((e) => bits & e.tags[j])
                        }
                    }

                    // Marks active tags
                    let eventsMask = 0;
                    groupEvents.forEach((e) => eventsMask |= e.tags[i]);
                    group.tags.forEach((t) => t.active = eventsMask & t.bit);

                    // Filters gant events
                    let apply = applyTags[i] & group.bits;
                    if (apply) {
                        events = events.filter((e) => apply & e.tags[i]);
                    }
                }

                // Reset counter
                this.eventCounter = events.length;
                this.filterCounter = (
                    this.applyTags.reduce((a, g) => a + g.length, 0)
                    + (this.applySearch.length > 0)
                );
                if (!events.length) {
                    self.filteredEvents = events;
                    return events;
                }

                events = masonry(events);

                // Doesn't show events under 1000px - that's too much
                if (!this.filterCounter) {
                    events = events.filter((e) => e.voffset < 800);
                }

                this.months = getMonths(events, today, weekendList, noWeekendList);
                this.width = this.months.reduce((r, m) => r + m.days.length, 0) * dayWidth;
                this.height = events.reduce((r, e) => Math.max(r, e.voffset), 0) + eventHeight + 20;

                // Renders background weekend stripes
                let strip_i = 0;
                this.stripes = []
                this.months.map(function(month){
                    month.days.map(function(day){
                        if (strip_i && self.stripes[strip_i - 1].is_weekend === day.is_weekend){
                            self.stripes[strip_i - 1].width += dayWidth;
                        } else {
                            self.stripes.push({
                                is_weekend: day.is_weekend,
                                width: dayWidth,
                            })
                            strip_i++;
                        }
                    });
                });
                this.filteredEvents = events;
                return events;
            }
        },
        methods: {
            addToCal: function(event){
                let start = event.start.format('YYYYMMDD'),
                    end = event.end.clone().add(1, 'days').format('YYYYMMDD'),
                    details = `🔗 ${event.url}`
                ;

                if (event.price) {
                    details += `\n🤑 ${event.price}`;
                }

                return (
                    `https://calendar.google.com/calendar/r/eventedit?`
                    + `text=${encodeURIComponent(event.title)}`
                    + `&dates=${start}/${end}`
                    + `&details=${encodeURIComponent(details)}`
                )
            },
            clearFilters: function(){
                this.applyTags = Array.from({length: this.tags.length}, () => []);
                this.applySearch = '';
            },
            showMenu: function(){
                this.menu.mobile = true;
                updateUrl(null, '');
            },
            hideMenu: function (){
                this.menu.mobile = false;
                updateUrl(null, '');
            },
            detailUrl: function(eventId){
                return buildUrl(null, eventId);
            },
            showDetail: function(eventId){
                let index = null,
                    event = null;

                for (let i = 0; i < this.filteredEvents.length; i++){
                    if (this.filteredEvents[i].id === eventId){
                        index = i;
                        event = this.filteredEvents[i];
                        break;
                    }
                }

                this.detail.event = event;
                this.detail.prev = this.filteredEvents[index - 1] || null;
                this.detail.next = this.filteredEvents[index + 1] || null;
                updateUrl(null, event ? event.id.toString() : '');
            },
            hideDetail: function(){
                updateUrl(null, '')
                this.detail.event = null;
            },
            parseUrl: function(value){
                return new URL(value);
            },
            formatPeriod: function(start, end){
                let result = start.date().toString();
                if (start.month() != end.month()){
                    result += ' ' + monthDeclensions[start.month()];
                }

                if (start.date() != end.date()){
                    if(isNaN(result)) {
                        result += ' — ';
                    } else {
                        result += '–';
                    }
                    result += end.date();
                }
                return result += ' ' + monthDeclensions[end.month()];
            },
            eventTags: function (event) {
                const tags = [];
                for (let i = 0; i < tagGroups.length; i++){
                    for (let j = 0; j < tagGroups[i].tags.length; j++){
                        const tag = tagGroups[i].tags[j]
                        if (event.tags[i] & tag.bit) {
                            tags.push(tag);
                        }
                    }
                }
                return tags;
            },
            goToTag: function (tag) {
                this.hideDetail();
                this.clearFilters();
                this.applyTags[tag.index].push(tag.bit);
            }
        }
    });

    // Disable back button
    window.addEventListener('popstate', function() {
        app.hideDetail();
        app.hideMenu();
    });
}

function buildUrl(params, hash){
    let url = new URL(window.location.href);

    switch (params) {
        case null:
            break;
        case '':
            url.search = '';
            break;
        default:
            url.search = '?' + params;
    }

    switch (hash) {
        case null:
            break;
        case '':
            url.hash = '';
            break;
        default:
            url.hash = '#' + hash;
    }

    return url;
}

function updateUrl(params, hash){
    const url = buildUrl(params, hash).toString();
    window.history.pushState({urlPath: url}, '', url);
}

function tagsToParams(tags){
    return 't=' + btoa(tags.join(tagSep))
}

function getEvents(eventSource, tagGroups) {
    let eventList = [];

    for (let i = 0; i < eventSource.length; i++){
        let source = eventSource[i];
        start = moment.unix(source.start);
        end = moment.unix(source.end);
        const days = end.diff(start, 'days') + 1;
        event = Object.assign(source, {
            index: i,
            start: start,
              end: end,
            level: source.level,
             days: days,
          hoffset: 0,
          voffset: 0,
            width: days * dayWidth,
        });

        eventList.push(event);
    }

    // Must sort events
    // Smallest left, biggest right
    return eventList.sort(function(a,b) {
        if (a.start > b.start) {
            return 1;
        } else if (a.start.isSame(b.start)) {
            // Puts longest first
            return b.end - a.end;
        }
        return -1;
    });
}

function getMonths(events, today, weekendList, noWeekendList){
    const firstDate = events[0].start.clone(),
           lastDate = events.reduce((r, e) => r < e.end ? e.end : r, firstDate),
          monthList = []
    ;

    // Creates months ruler
    const monthLen = lastDate.clone().startOf('month').diff(firstDate.clone().startOf('month'), 'months');
    for (let i = 0; i <= monthLen; i++) {
        let month = moment(firstDate),
            days = [];
        month.add(i, 'month');

        let total = month.daysInMonth();
        for (let y = 0; y < total; y++){
            let d = moment(month);
            d.date(y + 1)

            if (d < firstDate || d > lastDate) {
                continue
            }

            const f = d.format(dateFormat);
            days.push({
                date: d,
                is_weekend: !noWeekendList.has(f) && (d.isoWeekday() >= 6 || weekendList.has(f)),
                is_today: today.isSame(d, 'date'),
            });
        }

        let name = monthNames[month.month()];
        if (month.year() > today.year()) {
            name = name + '<small> ' + month.year() + '</small>'
        }

        monthList.push({
            name: name,
            days: days,
        });
    }

    return monthList;
}

function masonry(eventList){
    let events = [],
        seen = [],
        startDate = eventList[0].start
    ;

    for (let i = 0; i < eventList.length; i++) {
        let event = eventList[i];
        event.hoffset = event.start.diff(startDate, 'days') * dayWidth;

        // Moves event down
        // if row place is already taken.
        let found = false;
        for (let y = 0; y < seen.length; y++) {
            let other = seen[y];

            if (other.end < event.start) {
                seen[y] = event;
                event.voffset = y * eventHeight;
                found = true;
                break;
            }
        }

        // If row is empty
        // sets event's end as right border
        if (!found){
            event.voffset = seen.length * eventHeight;
            seen.push(event);
        }
        events.push(event)
    }
    return events
}

// Init
renderTripper(new Set(DATA.weekendList), new Set(DATA.noWeekendList), DATA.eventSource, DATA.tagGroups);

// Displays gant and hides loader
setTimeout(function(){
    document.body.classList.add('active');
}, 1000);

setTimeout(function(){
    let blocker = document.getElementById('blocker');
    blocker.parentNode.removeChild(blocker);
}, 1200);
